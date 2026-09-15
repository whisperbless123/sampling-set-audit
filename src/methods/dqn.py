"""Frozen M2 DQN sequential sampling-set selector."""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from typing import Any

import networkx as nx
import numpy as np
import torch
from torch import nn


class NodeQNetwork(nn.Module):
    """Shared node scorer with the protocol's two 128-unit hidden layers."""

    def __init__(self) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(11, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.layers(features).squeeze(-1)


def select(
    graph: nx.Graph,
    eigenvectors: np.ndarray,
    k: int,
    seed: int,
    objective: Callable[[np.ndarray], float],
    evaluation_budget: int = 2000,
    device: str = "cpu",
) -> tuple[np.ndarray, float, dict[str, Any]]:
    """Run the frozen sequential DQN and consume one objective call per episode.

    Unspecified engineering choices are fixed, not tuned: Adam, Huber loss,
    batch size 64, one replay update per episode, and terminal-only reward.
    """
    if evaluation_budget not in {500, 2000, 8000}:
        raise ValueError("the frozen DQN protocol allows E in {500, 2000, 8000}")
    if graph.number_of_nodes() != 100 or k not in {5, 10, 20}:
        raise ValueError("the authorized v6 DQN scope is N=100, k in {5, 10, 20}")
    torch_device = torch.device(device)
    torch.manual_seed(seed)
    np_rng = np.random.default_rng(seed)
    torch.use_deterministic_algorithms(True)
    if torch.backends.cudnn.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    torch.set_num_threads(1)

    nodes = list(range(100))
    degree = np.asarray([graph.degree(node) for node in nodes], dtype=np.float32)
    degree /= max(float(degree.max()), 1.0)
    clustering_map = nx.clustering(graph, nodes=nodes)
    clustering = np.asarray([clustering_map[node] for node in nodes], dtype=np.float32)
    spectral = np.asarray(eigenvectors[:, :8], dtype=np.float32)
    static_head = np.column_stack([degree, clustering]).astype(np.float32)
    adjacency = nx.to_numpy_array(graph, nodelist=nodes, dtype=np.float32)

    online = NodeQNetwork().to(torch_device)
    target = NodeQNetwork().to(torch_device)
    target.load_state_dict(online.state_dict())
    target.eval()
    optimizer = torch.optim.Adam(online.parameters(), lr=1e-3)
    replay: deque[tuple[np.ndarray, int, float, np.ndarray, bool]] = deque(maxlen=10_000)
    batch_size = 64
    timings = {
        "forward_seconds": 0.0,
        "backward_seconds": 0.0,
        "replay_sample_seconds": 0.0,
        "replay_write_seconds": 0.0,
        "target_sync_seconds": 0.0,
    }
    optimizer_steps = 0
    best_samples: np.ndarray | None = None
    best_score = float("inf")

    def feature_tensor(masks: np.ndarray) -> torch.Tensor:
        if masks.ndim == 1:
            masks = masks[None, :]
        neighbor_counts = masks.astype(np.float32) @ adjacency.T / float(k)
        head = np.broadcast_to(static_head, (masks.shape[0], *static_head.shape))
        eig = np.broadcast_to(spectral, (masks.shape[0], *spectral.shape))
        features = np.concatenate([head, neighbor_counts[:, :, None], eig], axis=2)
        return torch.as_tensor(features, dtype=torch.float32, device=torch_device)

    for episode in range(evaluation_budget):
        if episode < int(0.60 * evaluation_budget):
            epsilon = 1.0 - (1.0 - 0.05) * episode / max(int(0.60 * evaluation_budget) - 1, 1)
        else:
            epsilon = 0.05
        selected = np.zeros(100, dtype=bool)
        trajectory: list[tuple[np.ndarray, int, np.ndarray, bool]] = []
        for step in range(k):
            state = selected.copy()
            available = np.flatnonzero(~selected)
            if float(np_rng.random()) < epsilon:
                action = int(np_rng.choice(available))
            else:
                started = time.perf_counter()
                with torch.no_grad():
                    q_values = online(feature_tensor(selected))[0]
                    mask = torch.as_tensor(selected, dtype=torch.bool, device=torch_device)
                    q_values = q_values.masked_fill(mask, -torch.inf)
                    action = int(torch.argmax(q_values).item())
                timings["forward_seconds"] += time.perf_counter() - started
            selected[action] = True
            trajectory.append((state, action, selected.copy(), step == k - 1))

        samples = np.flatnonzero(selected)
        score = float(objective(samples))
        if score < best_score:
            best_score = score
            best_samples = samples.copy()
        started = time.perf_counter()
        for state, action, next_state, done in trajectory:
            replay.append((state, action, -score if done else 0.0, next_state, done))
        timings["replay_write_seconds"] += time.perf_counter() - started

        if len(replay) >= batch_size:
            started = time.perf_counter()
            indices = np_rng.choice(len(replay), size=batch_size, replace=False)
            batch = [replay[int(index)] for index in indices]
            states = np.stack([item[0] for item in batch])
            actions = torch.as_tensor([item[1] for item in batch], dtype=torch.long, device=torch_device)
            rewards = torch.as_tensor([item[2] for item in batch], dtype=torch.float32, device=torch_device)
            next_states = np.stack([item[3] for item in batch])
            dones = torch.as_tensor([item[4] for item in batch], dtype=torch.bool, device=torch_device)
            timings["replay_sample_seconds"] += time.perf_counter() - started

            started = time.perf_counter()
            q_current = online(feature_tensor(states)).gather(1, actions[:, None]).squeeze(1)
            with torch.no_grad():
                q_next_all = target(feature_tensor(next_states))
                invalid = torch.as_tensor(next_states, dtype=torch.bool, device=torch_device)
                q_next_all = q_next_all.masked_fill(invalid, -torch.inf)
                has_action = (~invalid).any(dim=1)
                q_next = torch.where(has_action, q_next_all.max(dim=1).values, torch.zeros_like(rewards))
                targets = rewards + (~dones).float() * q_next
            loss = nn.functional.smooth_l1_loss(q_current, targets)
            timings["forward_seconds"] += time.perf_counter() - started

            started = time.perf_counter()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            optimizer_steps += 1
            timings["backward_seconds"] += time.perf_counter() - started
            if optimizer_steps % 200 == 0:
                started = time.perf_counter()
                target.load_state_dict(online.state_dict())
                timings["target_sync_seconds"] += time.perf_counter() - started

    if best_samples is None or not np.isfinite(best_score):
        raise RuntimeError("DQN produced no finite candidate")
    return best_samples, best_score, {
        **timings,
        "optimizer_steps": optimizer_steps,
        "episodes": evaluation_budget,
        "replay_capacity": 10_000,
        "replay_final_size": len(replay),
        "target_update_steps": 200,
        "batch_size": batch_size,
        "updates_per_episode": 1,
        "loss": "smooth_l1",
        "optimizer": "Adam",
        "terminal_reward_only": True,
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "device": str(torch_device),
    }

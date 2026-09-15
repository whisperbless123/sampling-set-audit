"""Single reconstruction gateway and auditable pipeline-evaluation counter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import networkx as nx
import numpy as np

from src.reconstruct import lapreg_reconstruct
from src.signals import laplacian_eigh, s1, s2, s3


DEFAULT_RECONSTRUCTOR = lapreg_reconstruct
_EVAL_COUNT = 0


def reset() -> None:
    global _EVAL_COUNT
    _EVAL_COUNT = 0


def eval_count() -> int:
    return _EVAL_COUNT


def _laplacian(graph: nx.Graph) -> np.ndarray:
    return nx.laplacian_matrix(graph, nodelist=sorted(graph.nodes())).toarray().astype(float)


def _one_signal(
    graph: nx.Graph,
    family: str,
    seed: int,
    spectral: tuple[np.ndarray, np.ndarray],
) -> np.ndarray:
    family = family.upper()
    if family == "S1":
        return s1(graph, 1, seed, spectral=spectral)[:, 0]
    if family == "S2":
        return s2(graph, 1, seed, spectral=spectral)[:, 0]
    if family == "S3":
        return s3(graph, 1, seed, spectral=spectral)[:, 0]
    raise ValueError(f"unknown signal family: {family}")


def _score(samples: Sequence[int], ctx: Mapping[str, Any], seeds: Sequence[int]) -> float:
    sample_index = np.asarray(samples, dtype=int)
    graph_eval = ctx.get("graph_eval", ctx["graph_sel"])
    spectral = ctx.get("spectral_eval")
    if spectral is None:
        spectral = laplacian_eigh(graph_eval)
    signals = np.column_stack(
        [
            _one_signal(graph_eval, str(ctx["signal_family"]), int(seed), spectral)
            for seed in seeds
        ]
    )
    observations = signals[sample_index, :].copy()
    snr_db = ctx.get("snr_db", 20.0)
    if snr_db is not None:
        for column, seed in enumerate(seeds):
            rng = np.random.default_rng(int(seed) + 10_000_000)
            sigma = np.sqrt(np.mean(signals[:, column] ** 2)) / (10 ** (snr_db / 20))
            observations[:, column] += rng.normal(0.0, sigma, sample_index.size)
    laplacian_sel = ctx.get("laplacian_sel")
    if laplacian_sel is None:
        laplacian_sel = _laplacian(ctx["graph_sel"])
    estimate = DEFAULT_RECONSTRUCTOR(
        sample_index,
        observations,
        laplacian_sel,
        float(ctx["mu"]),
    )
    numerator = np.sum((estimate - signals) ** 2, axis=0)
    denominator = np.sum(signals**2, axis=0)
    return float(np.mean(numerator / denominator))


def evaluate(samples: Sequence[int], ctx: Mapping[str, Any]) -> float:
    """Count and perform one 32-signal candidate-set pipeline evaluation."""
    global _EVAL_COUNT
    _EVAL_COUNT += 1
    seeds = ctx.get("signal_seeds")
    if seeds is None:
        base = int(ctx.get("signal_seed", 0))
        seeds = list(range(base, base + 32))
    if len(seeds) != 32:
        raise ValueError("a pipeline evaluation must contain exactly 32 signals")
    return _score(samples, ctx, seeds)


def score_test_set(
    samples: Sequence[int], ctx: Mapping[str, Any], signal_seeds: Sequence[int]
) -> float:
    """Score a held-out test set without charging a method-selection evaluation."""
    return _score(samples, ctx, signal_seeds)

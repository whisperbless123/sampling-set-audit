"""A-24#1 analytic-risk oracle diagnostic with a preregistered MC bridge."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import networkx as nx
import numpy as np

from src.graphs import generate_graph
from src.methods.random_sel import select as random_select


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runs" / "oracle_risk_diagnostic.json"
EPSILON = 1e-2
MC_SAMPLES = 50_000
MC_BATCH = 1_000
MC_RELATIVE_TOLERANCE = 0.03
METHODS = ("Random", "Degree", "B3a", "B3b", "B3c", "CEM")


def require_environment() -> None:
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        if os.environ.get(key) != "1":
            raise RuntimeError(f"{key} must be 1")


def frozen_mu(graph_family: str) -> float:
    payload = json.loads(
        (ROOT / "runs" / "mu_calibration_v2.json").read_text(encoding="utf-8")
    )
    return float(payload["combinations"][f"{graph_family}_S2"]["value"])


def matrices(graph_family: str, graph_seed: int) -> dict[str, np.ndarray | float | list[set[int]]]:
    graph = generate_graph(graph_family, 100, graph_seed)
    laplacian = nx.laplacian_matrix(graph, nodelist=range(100)).toarray().astype(float)
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    covariance_eigenvalues = 1.0 / (eigenvalues + EPSILON)
    covariance = (eigenvectors * covariance_eigenvalues) @ eigenvectors.T
    covariance_sqrt = (eigenvectors * np.sqrt(covariance_eigenvalues)) @ eigenvectors.T
    sigma2 = float(np.trace(covariance) / 100.0 / 100.0)
    return {
        "laplacian": laplacian,
        "covariance": covariance,
        "covariance_sqrt": covariance_sqrt,
        "sigma2": sigma2,
        "components": [set(part) for part in nx.connected_components(graph)],
    }


def analytic_risk(samples: np.ndarray, mu: float, data: dict[str, object]) -> float:
    sample_set = set(int(node) for node in samples)
    if any(not sample_set.intersection(component) for component in data["components"]):
        raise np.linalg.LinAlgError("a connected component has no sampled node")
    laplacian = np.asarray(data["laplacian"])
    covariance = np.asarray(data["covariance"])
    indicator = np.zeros(100, dtype=float)
    indicator[np.asarray(samples, dtype=int)] = 1.0
    system = mu * laplacian + np.diag(indicator)
    if np.linalg.matrix_rank(system) != 100:
        raise np.linalg.LinAlgError("A_S is singular")
    inverse = np.linalg.solve(system, np.eye(100))
    first = mu**2 * np.trace(inverse @ laplacian @ covariance @ laplacian @ inverse)
    second = float(data["sigma2"]) * np.trace(inverse @ np.diag(indicator) @ inverse)
    return float(first + second)


def monte_carlo_risk(
    samples: np.ndarray, mu: float, data: dict[str, object], seed: int
) -> float:
    rng = np.random.default_rng(seed)
    laplacian = np.asarray(data["laplacian"])
    covariance_sqrt = np.asarray(data["covariance_sqrt"])
    indicator = np.zeros(100, dtype=float)
    indicator[np.asarray(samples, dtype=int)] = 1.0
    system = mu * laplacian + np.diag(indicator)
    inverse = np.linalg.solve(system, np.eye(100))
    squared_error = 0.0
    completed = 0
    while completed < MC_SAMPLES:
        count = min(MC_BATCH, MC_SAMPLES - completed)
        signals = covariance_sqrt @ rng.standard_normal((100, count))
        sigma = np.sqrt(np.mean(signals**2, axis=0)) / 10.0
        noise = rng.standard_normal((samples.size, count)) * sigma[None, :]
        right_hand_side = np.zeros((100, count), dtype=float)
        right_hand_side[samples, :] = signals[samples, :] + noise
        estimates = inverse @ right_hand_side
        squared_error += float(np.sum((estimates - signals) ** 2))
        completed += count
    return squared_error / MC_SAMPLES


def local_search(
    initial: np.ndarray, mu: float, data: dict[str, object]
) -> tuple[np.ndarray, float, int, int]:
    current = np.sort(np.asarray(initial, dtype=int))
    current_risk = analytic_risk(current, mu, data)
    iterations = 0
    evaluations = 1
    while True:
        selected = set(int(node) for node in current)
        best_key: tuple[float, int, int] | None = None
        best_samples: np.ndarray | None = None
        for removed in sorted(selected):
            for added in range(100):
                if added in selected:
                    continue
                candidate = np.asarray(sorted((selected - {removed}) | {added}), dtype=int)
                value = analytic_risk(candidate, mu, data)
                evaluations += 1
                key = (value, removed, added)
                if best_key is None or key < best_key:
                    best_key = key
                    best_samples = candidate
        assert best_key is not None and best_samples is not None
        if best_key[0] >= current_risk - 1e-12:
            return current, current_risk, iterations, evaluations
        current = best_samples
        current_risk = best_key[0]
        iterations += 1


def d0_rows(graph_family: str) -> list[dict[str, object]]:
    suffix = "_muREV" if graph_family == "G1" else ""
    path = ROOT / "runs" / f"d0_{graph_family}_S2_k10_N100{suffix}.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 70:
        raise RuntimeError(f"unexpected baseline row count in {path}: {len(rows)}")
    return rows


def cem_rows(graph_family: str) -> list[dict[str, object]]:
    suffix = "_muREV" if graph_family == "G1" else ""
    path = ROOT / "runs" / "sealed" / f"cem_d0_{graph_family}_S2_k10_N100{suffix}.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 30:
        raise RuntimeError(f"unexpected CEM row count in {path}: {len(rows)}")
    return rows


def main() -> None:
    require_environment()
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")

    # The MC bridge is completed and checked before any local search begins.
    bridge: list[dict[str, object]] = []
    for family_index, graph_family in enumerate(("G1", "G2", "G3")):
        mu = frozen_mu(graph_family)
        for graph_seed in (0, 1):
            data = matrices(graph_family, graph_seed)
            sample_seed = 24_100 + 100 * family_index + graph_seed
            samples = random_select(100, 10, sample_seed)
            analytic = analytic_risk(samples, mu, data)
            mc_seed = 24_200 + 100 * family_index + graph_seed
            estimate = monte_carlo_risk(samples, mu, data, mc_seed)
            relative = abs(estimate - analytic) / analytic
            bridge.append(
                {
                    "graph_family": graph_family,
                    "graph_seed": graph_seed,
                    "sample_seed": sample_seed,
                    "samples": samples.tolist(),
                    "mc_seed": mc_seed,
                    "analytic_risk": analytic,
                    "mc_risk": estimate,
                    "relative_deviation": relative,
                    "passed": relative <= MC_RELATIVE_TOLERANCE,
                }
            )
    if not all(bool(row["passed"]) for row in bridge):
        raise RuntimeError("MC bridge exceeded the preregistered relative tolerance")

    cells: list[dict[str, object]] = []
    for graph_family in ("G1", "G2", "G3"):
        mu = frozen_mu(graph_family)
        baselines = d0_rows(graph_family)
        cems = cem_rows(graph_family)
        graph_results: list[dict[str, object]] = []
        for graph_seed in range(10):
            data = matrices(graph_family, graph_seed)
            start_seed = 0
            initial = random_select(100, 10, start_seed)
            started = time.perf_counter()
            oracle_samples, oracle_value, iterations, risk_evaluations = local_search(
                initial, mu, data
            )
            elapsed = time.perf_counter() - started
            method_values: dict[str, dict[str, object]] = {}
            source_rows = [
                row for row in baselines if int(row["graph_seed"]) == graph_seed
            ] + [row for row in cems if int(row["graph_seed"]) == graph_seed]
            for method in METHODS:
                selected_rows = [row for row in source_rows if row["method"] == method]
                expected = 3 if method in {"Random", "CEM"} else 1
                if len(selected_rows) != expected:
                    raise RuntimeError(
                        f"{graph_family} seed {graph_seed} {method}: {len(selected_rows)} rows"
                    )
                runs = [
                    {
                        "method_seed": row.get("method_seed"),
                        "samples": row["samples"],
                        "risk": analytic_risk(
                            np.asarray(row["samples"], dtype=int), mu, data
                        ),
                    }
                    for row in selected_rows
                ]
                method_values[method] = {
                    "runs": runs,
                    "per_graph_risk": float(np.mean([run["risk"] for run in runs])),
                }
            graph_results.append(
                {
                    "graph_seed": graph_seed,
                    "random_start_seed": start_seed,
                    "random_start_samples": initial.tolist(),
                    "oracle_samples": oracle_samples.tolist(),
                    "oracle_risk": oracle_value,
                    "local_search_iterations": iterations,
                    "risk_evaluations": risk_evaluations,
                    "wall_seconds": elapsed,
                    "methods": method_values,
                }
            )

        method_vectors = {
            method: np.asarray(
                [row["methods"][method]["per_graph_risk"] for row in graph_results],
                dtype=float,
            )
            for method in METHODS
        }
        method_means = {method: float(np.mean(values)) for method, values in method_vectors.items()}
        best_method = min(METHODS, key=lambda method: (method_means[method], method))
        oracle_vector = np.asarray([row["oracle_risk"] for row in graph_results], dtype=float)
        deployment_vector = method_vectors[best_method]
        gain = float(np.mean(deployment_vector - oracle_vector))
        readings: dict[str, object] = {}
        exits: list[str] = []
        for ddof in (0, 1):
            delta = float(
                3.0
                * (
                    np.std(deployment_vector, ddof=ddof)
                    + np.std(oracle_vector, ddof=ddof)
                )
            )
            exit_name = "A" if gain <= delta else "B"
            exits.append(exit_name)
            readings[f"ddof_{ddof}"] = {"delta": delta, "exit": exit_name}
        if len(set(exits)) != 1:
            raise RuntimeError(f"DDOF_SPLIT in {graph_family}_S2")
        cells.append(
            {
                "cell": f"{graph_family}_S2_D0_k10_N100",
                "mu": mu,
                "oracle_label": "one-swap local-search risk oracle",
                "best_deployment_method": best_method,
                "method_cross_graph_mean_risk": method_means,
                "oracle_cross_graph_mean_risk": float(np.mean(oracle_vector)),
                "oracle_gain_unnormalized": gain,
                "readings": readings,
                "DDOF_SPLIT": False,
                "exit": exits[0],
                "graphs": graph_results,
            }
        )

    payload = {
        "authorization": "A-24 item 1",
        "gate_commit": "1da95590313fd321f6e60695aff8db0abc5faeaa",
        "risk_definition": (
            "mu^2 tr(A^-1 L Sigma L A^-1) + sigma^2 tr(A^-1 D A^-1)"
        ),
        "sigma2_definition": "E[per-signal RMS^2]/100 = tr(Sigma)/(N*100) at 20 dB",
        "normalization": "none",
        "mc_bridge": {
            "samples_per_case": MC_SAMPLES,
            "relative_tolerance": MC_RELATIVE_TOLERANCE,
            "completed_before_search": True,
            "cases": bridge,
        },
        "cells": cells,
        "competition_exclusion": "diagnostic only; excluded from K2/K3/K4/K4-b and the 15 method pairs",
        "git_commit_at_generation": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT
        )
        .decode()
        .strip(),
        "thread_config": {
            key: os.environ[key]
            for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "bridge_max_relative_deviation": max(
                    row["relative_deviation"] for row in bridge
                ),
                "exits": {cell["cell"]: cell["exit"] for cell in cells},
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

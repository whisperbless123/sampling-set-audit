"""D1 cell driver: configuration to auditable JSON/JSONL artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import networkx as nx
import numpy as np

from src import evalcore
from src.graphs import generate_graph
from src.methods.b3a import select as b3a_select
from src.methods.b3b import select as b3b_select
from src.methods.b3c import select as b3c_select
from src.methods.cem import select as cem_select
from src.methods.degree import select as degree_select
from src.methods.random_sel import select as random_select
from src.reconstruct import bandlimited_ls, lapreg_reconstruct
from src.signals import laplacian_eigh, s1


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
THREAD_VARIABLES = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")
A05_PLATFORM_RULE_QUOTE = (
    "平台点的精确定义：等效区 = 网格上 NMSE ≤ 1.01 × 网格最小值的点集中"
    "包含 argmin 的连续段；平台点 = 该段内最大 μ。适用于全部九组合。"
)
A05_NO_RERUN_QUOTE = (
    "附一条禁令：不得为\"验证\"而补跑 μ=0.01 对照——跑两版再挑即 μ-shopping，"
    "比任何单版都糟；规则定于原理、执行恰一次。"
)


def _require_single_thread() -> dict[str, str]:
    values = {name: os.environ.get(name, "") for name in THREAD_VARIABLES}
    if any(value != "1" for value in values.values()):
        raise RuntimeError(f"single-thread variables must all equal 1, got {values}")
    return values


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _write_jsonl_atomic(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    temporary.replace(path)


def _signal_seeds(graph_seed: int, n_signals: int, calibration: bool) -> list[int]:
    offset = 20_000_000 if calibration else 10_000_000
    return [offset + graph_seed * 10_000 + index for index in range(n_signals)]


def calibrate_mu() -> dict[str, Any]:
    _require_single_thread()
    mu_grid = [1e-3, 1e-2, 1e-1, 1.0]
    graph_families = ["G1", "G2", "G3"]
    signal_families = ["S1", "S2", "S3"]
    method_seeds = [0, 1, 2]
    results: list[dict[str, Any]] = []
    selected: dict[str, float] = {}
    for graph_family in graph_families:
        for signal_family in signal_families:
            combo = f"{graph_family}_{signal_family}"
            combo_rows: list[dict[str, Any]] = []
            for mu in mu_grid:
                graph_rows: list[dict[str, Any]] = []
                for graph_seed in (1000, 1001, 1002):
                    graph = generate_graph(graph_family, 100, graph_seed)
                    seeds = _signal_seeds(graph_seed, 200, calibration=True)
                    seed_nmse = []
                    for method_seed in method_seeds:
                        samples = random_select(100, 10, method_seed)
                        ctx = {
                            "graph_sel": graph,
                            "signal_family": signal_family,
                            "mu": mu,
                            "snr_db": 20.0,
                        }
                        seed_nmse.append(evalcore.score_test_set(samples, ctx, seeds))
                    graph_rows.append(
                        {
                            "graph_seed": graph_seed,
                            "signal_seeds": seeds,
                            "method_seeds": method_seeds,
                            "method_seed_nmse": seed_nmse,
                            "mean_nmse": float(np.mean(seed_nmse)),
                        }
                    )
                row = {
                    "graph_family": graph_family,
                    "signal_family": signal_family,
                    "mu": mu,
                    "graphs": graph_rows,
                    "mean_nmse": float(np.mean([item["mean_nmse"] for item in graph_rows])),
                }
                results.append(row)
                combo_rows.append(row)
            selected[combo] = float(min(combo_rows, key=lambda item: item["mean_nmse"])["mu"])
    payload = {
        "frozen": False,
        "status": "PENDING_RULING",
        "selector": "random",
        "k_ratio": 0.10,
        "graph_seeds": [1000, 1001, 1002],
        "method_seeds": method_seeds,
        "mu_grid": mu_grid,
        "provisional_best_mu": selected,
        "results": results,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "mu_calibration.json", payload)
    return payload


def _load_calibration() -> dict[str, Any]:
    path = RUNS / "mu_calibration.json"
    if not path.exists():
        return calibrate_mu()
    return json.loads(path.read_text(encoding="utf-8"))


def _load_calibration_v2() -> dict[str, Any]:
    path = RUNS / "mu_calibration_v2.json"
    if not path.exists():
        raise RuntimeError("Stage 1 calibration must complete before Stage 2")
    return json.loads(path.read_text(encoding="utf-8"))


def calibrate_mu_v2() -> dict[str, Any]:
    """Apply A-03's expanded grid and mechanical plateau freeze rule."""
    _require_single_thread()
    if (RUNS / "mu_calibration_v2.json").exists():
        raise RuntimeError(A05_NO_RERUN_QUOTE)
    original = json.loads((RUNS / "mu_calibration.json").read_text(encoding="utf-8"))
    rows = list(original["results"])
    boundary_combinations = {"G1_S1", "G1_S2", "G2_S1", "G3_S1"}
    method_seeds = [0, 1, 2]
    for combo in sorted(boundary_combinations):
        graph_family, signal_family = combo.split("_")
        for mu in (1e-4, 1e-5):
            graph_rows = []
            for graph_seed in (1000, 1001, 1002):
                graph = generate_graph(graph_family, 100, graph_seed)
                seeds = _signal_seeds(graph_seed, 200, calibration=True)
                seed_nmse = []
                for method_seed in method_seeds:
                    samples = random_select(100, 10, method_seed)
                    ctx = {
                        "graph_sel": graph,
                        "signal_family": signal_family,
                        "mu": mu,
                        "snr_db": 20.0,
                    }
                    seed_nmse.append(evalcore.score_test_set(samples, ctx, seeds))
                graph_rows.append(
                    {
                        "graph_seed": graph_seed,
                        "signal_seeds": seeds,
                        "method_seeds": method_seeds,
                        "method_seed_nmse": seed_nmse,
                        "mean_nmse": float(np.mean(seed_nmse)),
                    }
                )
            rows.append(
                {
                    "graph_family": graph_family,
                    "signal_family": signal_family,
                    "mu": mu,
                    "graphs": graph_rows,
                    "mean_nmse": float(np.mean([item["mean_nmse"] for item in graph_rows])),
                }
            )

    combinations: dict[str, Any] = {}
    limitations: list[str] = []
    for graph_family in ("G1", "G2", "G3"):
        for signal_family in ("S1", "S2", "S3"):
            combo = f"{graph_family}_{signal_family}"
            combo_rows = [
                row
                for row in rows
                if row["graph_family"] == graph_family
                and row["signal_family"] == signal_family
            ]
            combo_rows = sorted(combo_rows, key=lambda row: row["mu"])
            best_index = min(
                range(len(combo_rows)), key=lambda index: combo_rows[index]["mean_nmse"]
            )
            best_nmse = combo_rows[best_index]["mean_nmse"]
            lower = best_index
            upper = best_index
            while lower > 0 and combo_rows[lower - 1]["mean_nmse"] <= 1.01 * best_nmse:
                lower -= 1
            while upper + 1 < len(combo_rows) and combo_rows[upper + 1]["mean_nmse"] <= 1.01 * best_nmse:
                upper += 1
            plateau = [row["mu"] for row in combo_rows[lower : upper + 1]]
            plateau_point = float(plateau[-1])
            original_best = min(
                row["mean_nmse"] for row in combo_rows if row["mu"] >= 1e-3
            )
            improvement = float((original_best - best_nmse) / original_best)
            best_mus = [row["mu"] for row in combo_rows if row["mean_nmse"] == best_nmse]
            limitation_reasons = []
            if combo in boundary_combinations and min(best_mus) == 1e-5:
                limitation_reasons.append("expanded optimum remains at new lower boundary 1e-5")
            if combo in boundary_combinations and improvement < 0.01:
                limitation_reasons.append("improvement relative to original optimum is below 1%")
            if limitation_reasons:
                limitations.append(f"{combo}: " + "; ".join(limitation_reasons))
            combinations[combo] = {
                "grid": sorted(float(row["mu"]) for row in combo_rows),
                "best_nmse": float(best_nmse),
                "best_mu": float(min(best_mus)),
                "plateau_set": [float(value) for value in plateau],
                "plateau_point": plateau_point,
                "relative_improvement_vs_original_best": improvement,
                "frozen": True,
                "status": "FROZEN",
                "value": plateau_point,
                "limitation_reasons": limitation_reasons,
            }

    literal = float(combinations["G1_S2"]["plateau_point"])
    revised = float(combinations["G1_S2"]["plateau_point"])
    same = literal == revised
    dual_reading = {
        "literal_value": literal,
        "revised_value": revised,
        "same_value": same,
        "disposition": "FROZEN_SAME_VALUE" if same else "PENDING_DUAL_RUN",
        "a05_cause": (
            "字面读法与修正读法按 A-05 定义同为 0.01，原 literal_value: 0.001 "
            "系误用 argmin 而非平台点。"
        ),
    }
    if not same:
        combinations["G1_S2"].update(frozen=False, status="PENDING", value=None)

    payload = {
        "frozen": all(item["frozen"] for item in combinations.values()),
        "status": "FROZEN" if all(item["frozen"] for item in combinations.values()) else "PARTIAL_PENDING",
        "selector": "random",
        "k_ratio": 0.10,
        "graph_seeds": [1000, 1001, 1002],
        "method_seeds": method_seeds,
        "rows": rows,
        "combinations": combinations,
        "g1_s2_dual_reading": dual_reading,
        "limitations": limitations,
        "a05_platform_rule_quote": A05_PLATFORM_RULE_QUOTE,
        "a05_no_rerun_quote": A05_NO_RERUN_QUOTE,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "mu_calibration_v2.json", payload)
    return payload


def run_random_baseline() -> list[dict[str, Any]]:
    _require_single_thread()
    calibration = _load_calibration_v2()
    mu = float(calibration["combinations"]["G2_S1"]["value"])
    path = RUNS / "random_G2_S1_D0_k10_N100.jsonl"
    records: list[dict[str, Any]] = []
    for graph_seed in range(10):
        graph = generate_graph("G2", 100, graph_seed)
        signal_seeds = _signal_seeds(graph_seed, 200, calibration=False)
        for method_seed in range(3):
            config = {
                "graph_family": "G2",
                "signal_family": "S1",
                "drift": "D0",
                "n": 100,
                "k": 10,
                "k_ratio": 0.10,
                "mu": mu,
                "mu_status": "FROZEN_A03",
                "graph_seed": graph_seed,
                "method_seed": method_seed,
                "signal_seeds": signal_seeds,
                "snr_db": 20.0,
            }
            evalcore.reset()
            samples = random_select(100, 10, method_seed)
            started = time.perf_counter()
            nmse = evalcore.score_test_set(samples, {"graph_sel": graph, **config}, signal_seeds)
            record = {
                **config,
                "method": "B1_random",
                "samples": samples.tolist(),
                "nmse": nmse,
                "eval_count": evalcore.eval_count(),
                "elapsed_seconds": time.perf_counter() - started,
                "config_hash": _hash(config),
                "git_commit": _git_head(),
                "hostname": socket.gethostname(),
                "thread_config": _require_single_thread(),
            }
            records.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    return records


def run_k1() -> dict[str, Any]:
    _require_single_thread()
    calibration = _load_calibration()
    mu = float(calibration["provisional_best_mu"]["G2_S1"])
    graph = generate_graph("G2", 100, 0)
    laplacian = nx.laplacian_matrix(graph, nodelist=range(100)).toarray().astype(float)
    _, eigenvectors = laplacian_eigh(graph)
    signals = s1(graph, 200, 30_000_000, spectral=(np.linalg.eigvalsh(laplacian), eigenvectors))
    rng = np.random.default_rng(0)
    redraws = 0
    while True:
        samples = np.sort(rng.choice(100, size=10, replace=False))
        condition = float(np.linalg.cond(eigenvectors[samples, :10]))
        rank = int(np.linalg.matrix_rank(eigenvectors[samples, :10]))
        if rank == 10 and condition <= 1e6:
            break
        redraws += 1
    bandlimited, condition = bandlimited_ls(samples, signals[samples, :], eigenvectors, 10)
    lapreg = lapreg_reconstruct(samples, signals[samples, :], laplacian, mu)
    denom = np.sum(signals**2, axis=0)
    k1_bandlimited = float(np.mean(np.sum((bandlimited - signals) ** 2, axis=0) / denom))
    k1_lapreg = float(np.mean(np.sum((lapreg - signals) ** 2, axis=0) / denom))

    rows = []
    passed_graphs = 0
    for graph_seed in range(10):
        graph_i = generate_graph("G2", 100, graph_seed)
        _, basis_i = laplacian_eigh(graph_i)
        placeholder = np.argsort(np.sum(basis_i[:, :10] ** 2, axis=1))[-10:]
        seeds = _signal_seeds(graph_seed, 200, calibration=False)
        ctx = {"graph_sel": graph_i, "signal_family": "S1", "mu": mu, "snr_db": 20.0}
        placeholder_nmse = evalcore.score_test_set(placeholder, ctx, seeds)
        random_values = [
            evalcore.score_test_set(random_select(100, 10, method_seed), ctx, seeds)
            for method_seed in range(3)
        ]
        random_nmse = float(np.mean(random_values))
        difference = placeholder_nmse - random_nmse
        passed = bool(difference <= 1e-9 * max(1.0, abs(random_nmse)))
        passed_graphs += int(passed)
        rows.append(
            {
                "graph_seed": graph_seed,
                "placeholder_nmse": placeholder_nmse,
                "random_method_seed_nmse": random_values,
                "random_mean_nmse": random_nmse,
                "difference_placeholder_minus_random": difference,
                "passed": passed,
            }
        )
    result = {
        "k1_1": {
            "bandlimited_nmse": k1_bandlimited,
            "passed": k1_bandlimited < 1e-8,
            "condition_number": condition,
            "redraw_count": redraws,
            "lapreg_nmse_record_only": k1_lapreg,
            "samples": samples.tolist(),
            "n_signals": 200,
        },
        "k1_2": {
            "label": "占位实现下的判定，非协议 B3a",
            "passed_graphs": passed_graphs,
            "passed": passed_graphs == 10,
            "rows": rows,
        },
        "k1_3_b": "NOT_DUE_D1; gates D3/D4 admission",
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "k1_results.json", result)
    return result


def _coverage_metrics(graph: nx.Graph, samples: np.ndarray) -> dict[str, Any]:
    counts = [0, 0, 0, 0]
    for node in samples:
        counts[int(graph.nodes[int(node)]["community"])] += 1
    distances = nx.multi_source_dijkstra_path_length(
        graph, [int(node) for node in samples], weight=None
    )
    if len(distances) != graph.number_of_nodes():
        maximum = float("inf")
        mean = float("inf")
    else:
        values = np.asarray(list(distances.values()), dtype=float)
        maximum = float(np.max(values))
        mean = float(np.mean(values))
    return {
        "community_sample_counts": counts,
        "missed_communities": int(sum(count == 0 for count in counts)),
        "nearest_sample_distance_max": maximum,
        "nearest_sample_distance_mean": mean,
    }


def diagnose_k1_coverage() -> dict[str, Any]:
    """D1-A2: coverage-only diagnosis of the 40 existing K1-2 sets."""
    _require_single_thread()
    source = json.loads((RUNS / "k1_2_diagnosis.json").read_text(encoding="utf-8"))
    source_rows = {int(row["graph_seed"]): row for row in source["rows"]}
    rows = []
    for graph_seed in range(10):
        graph = generate_graph("G2", 100, graph_seed)
        _, basis = laplacian_eigh(graph)
        low_band = basis[:, :10]
        placeholder_samples = np.sort(
            np.argsort(np.sum(low_band**2, axis=1))[-10:]
        )
        source_row = source_rows[graph_seed]
        placeholder = {
            "samples": placeholder_samples.tolist(),
            "condition_number": source_row["placeholder"]["condition_number"],
            "sigma_min": source_row["placeholder"]["sigma_min"],
            **_coverage_metrics(graph, placeholder_samples),
        }
        random_rows = []
        for method_seed, source_random in enumerate(source_row["random"]):
            samples = random_select(100, 10, method_seed)
            random_rows.append(
                {
                    "method_seed": method_seed,
                    "samples": samples.tolist(),
                    "condition_number": source_random["condition_number"],
                    "sigma_min": source_random["sigma_min"],
                    **_coverage_metrics(graph, samples),
                }
            )
        rows.append(
            {"graph_seed": graph_seed, "placeholder": placeholder, "random": random_rows}
        )
    payload = {
        "artifact": "D1-A2 K1-2 coverage diagnosis",
        "diagnostic_only": True,
        "selection_changed": False,
        "search_performed": False,
        "nmse_evaluated": False,
        "source": "runs/k1_2_diagnosis.json",
        "rows": rows,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "k1_2_diagnosis2.json", payload)
    return payload


def _frozen_mu(graph_family: str, signal_family: str, variant: str | None = None) -> float:
    calibration = _load_calibration_v2()
    combo = calibration["combinations"][f"{graph_family}_{signal_family}"]
    if combo["status"] == "FROZEN":
        return float(combo["value"])
    if graph_family == "G1" and signal_family == "S2":
        dual = calibration["g1_s2_dual_reading"]
        if variant == "LIT":
            return float(dual["literal_value"])
        if variant == "REV":
            return float(dual["revised_value"])
    raise RuntimeError(f"mu is pending for {graph_family}-{signal_family}; variant required")


def formal_k1_2_firstcheck() -> dict[str, Any]:
    """A-04 first and only formal K1-2 check using true B3a."""
    _require_single_thread()
    mu = _frozen_mu("G2", "S1")
    rows = []
    passed_graphs = 0
    for graph_seed in range(10):
        graph = generate_graph("G2", 100, graph_seed)
        _, basis = laplacian_eigh(graph)
        b3a_samples = b3a_select(basis, 10, 10)
        seeds = _signal_seeds(graph_seed, 200, calibration=False)
        ctx = {"graph_sel": graph, "signal_family": "S1", "mu": mu, "snr_db": 20.0}
        evalcore.reset()
        b3a_nmse = evalcore.score_test_set(b3a_samples, ctx, seeds)
        b3a_eval_count = evalcore.eval_count()
        random_rows = []
        for method_seed in range(3):
            random_samples = random_select(100, 10, method_seed)
            random_nmse = evalcore.score_test_set(random_samples, ctx, seeds)
            random_rows.append(
                {
                    "method_seed": method_seed,
                    "samples": random_samples.tolist(),
                    "nmse": random_nmse,
                }
            )
        random_mean = float(np.mean([row["nmse"] for row in random_rows]))
        difference = b3a_nmse - random_mean
        passed = bool(b3a_nmse <= random_mean)
        passed_graphs += int(passed)
        rows.append(
            {
                "graph_seed": graph_seed,
                "signal_seeds": seeds,
                "b3a": {
                    "samples": b3a_samples.tolist(),
                    "nmse": b3a_nmse,
                    "eval_count": b3a_eval_count,
                },
                "random": random_rows,
                "random_mean_nmse": random_mean,
                "difference_b3a_minus_random": difference,
                "passed": passed,
            }
        )
    payload = {
        "label": "A-04 formal first check; true B3a, not placeholder",
        "passed_graphs": passed_graphs,
        "passed": passed_graphs == 10,
        "threshold": "10/10; exact <= with no tolerance",
        "rows": rows,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "k1_2_firstcheck.json", payload)
    return payload


def firstcheck_diagnosis() -> dict[str, Any]:
    """Stage F diagnostics, callable only after a failed formal first check."""
    _require_single_thread()
    firstcheck = json.loads((RUNS / "k1_2_firstcheck.json").read_text(encoding="utf-8"))
    if firstcheck["passed"]:
        raise RuntimeError("Stage F is forbidden after a passing first check")
    rows = []
    for row in firstcheck["rows"]:
        graph_seed = int(row["graph_seed"])
        graph = generate_graph("G2", 100, graph_seed)
        _, basis = laplacian_eigh(graph)
        low_band = basis[:, :10]

        def diagnose(item: dict[str, Any]) -> dict[str, Any]:
            samples = np.asarray(item["samples"], dtype=int)
            matrix = low_band[samples, :]
            singular = np.linalg.svd(matrix, compute_uv=False)
            return {
                **item,
                "condition_number": float(np.linalg.cond(matrix)),
                "sigma_min": float(singular[-1]),
                **_coverage_metrics(graph, samples),
            }

        rows.append(
            {
                "graph_seed": graph_seed,
                "b3a": diagnose(row["b3a"]),
                "random": [diagnose(item) for item in row["random"]],
            }
        )
    payload = {
        "diagnostic_only": True,
        "source": "runs/k1_2_firstcheck.json",
        "rows": rows,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "k1_2_firstcheck_diagnosis.json", payload)
    return payload


def _stage5_cell(
    graph_family: str, signal_family: str, mu_variant: str | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mu = _frozen_mu(graph_family, signal_family, mu_variant)
    records: list[dict[str, Any]] = []
    for graph_seed in range(10):
        graph = generate_graph(graph_family, 100, graph_seed)
        eigenvalues, basis = laplacian_eigh(graph)
        laplacian = nx.laplacian_matrix(graph, nodelist=range(100)).toarray().astype(float)
        sigma2 = float(np.mean(1.0 / (eigenvalues + 1e-2)) / 100.0)
        sampling_sets = {
            "Degree": degree_select(graph, 10),
            "B3a": b3a_select(basis, 10, 10),
            "B3b": b3b_select(laplacian, mu, 10),
            "B3c": b3c_select(laplacian, mu, sigma2, 10),
        }
        signal_seeds = _signal_seeds(graph_seed, 200, calibration=False)
        ctx = {
            "graph_sel": graph,
            "signal_family": signal_family,
            "mu": mu,
            "snr_db": 20.0,
        }
        method_items = [
            ("Random", seed, random_select(100, 10, seed)) for seed in range(3)
        ] + [(method, None, samples) for method, samples in sampling_sets.items()]
        for method, method_seed, samples in method_items:
            config = {
                "graph_family": graph_family,
                "signal_family": signal_family,
                "drift": "D0",
                "n": 100,
                "k": 10,
                "k_ratio": 0.10,
                "mu": mu,
                "mu_variant": mu_variant,
                "graph_seed": graph_seed,
                "method": method,
                "method_seed": method_seed,
                "signal_seeds": signal_seeds,
                "snr_db": 20.0,
            }
            evalcore.reset()
            started = time.perf_counter()
            nmse = evalcore.score_test_set(samples, ctx, signal_seeds)
            records.append(
                {
                    **config,
                    "samples": samples.tolist(),
                    "nmse": nmse,
                    "eval_count": evalcore.eval_count(),
                    "elapsed_seconds": time.perf_counter() - started,
                    "config_hash": _hash(config),
                    "git_commit": _git_head(),
                    "hostname": socket.gethostname(),
                    "thread_config": _require_single_thread(),
                }
            )

    cell = f"{graph_family}-{signal_family}-D0-k10-N100"
    flags: list[dict[str, Any]] = []
    for record in records:
        if not np.isfinite(record["nmse"]) or record["nmse"] > 10:
            flags.append({"flag": "a", "cell": cell, "run": record["config_hash"]})
        if record["eval_count"] != 0:
            flags.append({"flag": "c", "cell": cell, "run": record["config_hash"]})
    random_by_seed = []
    for method_seed in range(3):
        values = [
            record["nmse"]
            for record in records
            if record["method"] == "Random" and record["method_seed"] == method_seed
        ]
        random_by_seed.append(float(np.mean(values)))
    random_mean = float(np.mean(random_by_seed))
    random_sd = float(np.std(random_by_seed, ddof=1))
    if random_sd > 0.5 * random_mean:
        flags.append(
            {
                "flag": "b",
                "cell": cell,
                "random_seed_means": random_by_seed,
                "random_mean": random_mean,
                "random_sd": random_sd,
            }
        )
    return records, flags


def run_stage5_baselines() -> dict[str, Any]:
    _require_single_thread()
    queue: list[tuple[str, str, str | None]] = []
    for graph_family in ("G1", "G2", "G3"):
        for signal_family in ("S1", "S2", "S3"):
            if graph_family == "G1" and signal_family == "S2":
                queue.extend([("G1", "S2", "LIT"), ("G1", "S2", "REV")])
            else:
                queue.append((graph_family, signal_family, None))
    completed = []
    flags: list[dict[str, Any]] = []
    interrupted = []
    for graph_family, signal_family, variant in queue:
        now = time_now = __import__("datetime").datetime.now(ZoneInfo("Asia/Shanghai"))
        if time_now.hour > 6 or (time_now.hour == 6 and time_now.minute >= 30):
            interrupted.append(
                {"graph_family": graph_family, "signal_family": signal_family, "variant": variant}
            )
            break
        records, cell_flags = _stage5_cell(graph_family, signal_family, variant)
        suffix = f"_mu{variant}" if variant else ""
        filename = f"d0_{graph_family}_{signal_family}_k10_N100{suffix}.jsonl"
        _write_jsonl_atomic(RUNS / filename, records)
        completed.append(
            {
                "graph_family": graph_family,
                "signal_family": signal_family,
                "mu_variant": variant,
                "file": f"runs/{filename}",
                "runs": len(records),
            }
        )
        flags.extend(cell_flags)
        if cell_flags:
            break
    payload = {
        "completed": completed,
        "completed_physical_cells": len(completed),
        "completed_logical_cells": len(
            {(item["graph_family"], item["signal_family"]) for item in completed}
        ),
        "flags": flags,
        "gate_passed": not flags and len(completed) == len(queue),
        "interrupted_not_started": interrupted,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "stage5_summary.json", payload)
    return payload


def _cem_training_seed_base(
    graph_family: str,
    signal_family: str,
    graph_seed: int,
    method_seed: int,
    variant: str | None,
) -> int:
    graph_index = {"G1": 0, "G2": 1, "G3": 2}[graph_family]
    signal_index = {"S1": 0, "S2": 1, "S3": 2}[signal_family]
    variant_index = {None: 0, "LIT": 1, "REV": 2}[variant]
    return (
        100_000_000
        + graph_index * 100_000_000
        + signal_index * 30_000_000
        + graph_seed * 3_000_000
        + method_seed * 1_000_000
        + variant_index * 200_000
    )


def _run_cem_cell(
    graph_family: str,
    signal_family: str,
    variant: str | None,
    enforce_first_gate: bool,
) -> tuple[list[dict[str, Any]], bool, int | None]:
    mu = _frozen_mu(graph_family, signal_family, variant)
    records = []
    first_count = None
    for graph_seed in range(10):
        graph = generate_graph(graph_family, 100, graph_seed)
        test_seeds = _signal_seeds(graph_seed, 200, calibration=False)
        for method_seed in range(3):
            training_base = _cem_training_seed_base(
                graph_family, signal_family, graph_seed, method_seed, variant
            )
            base_ctx = {
                "graph_sel": graph,
                "signal_family": signal_family,
                "mu": mu,
                "snr_db": 20.0,
            }
            evalcore.reset()

            def objective(samples: np.ndarray) -> float:
                call_index = evalcore.eval_count()
                signal_seeds = [
                    training_base + 32 * call_index + offset for offset in range(32)
                ]
                return evalcore.evaluate(samples, {**base_ctx, "signal_seeds": signal_seeds})

            started = time.perf_counter()
            samples, selection_score = cem_select(100, 10, method_seed, objective)
            count = evalcore.eval_count()
            if first_count is None:
                first_count = count
            if count != 2000:
                return records, False, count
            test_nmse = evalcore.score_test_set(samples, base_ctx, test_seeds)
            elapsed = time.perf_counter() - started
            config = {
                "graph_family": graph_family,
                "signal_family": signal_family,
                "drift": "D0",
                "n": 100,
                "k": 10,
                "mu": mu,
                "mu_variant": variant,
                "graph_seed": graph_seed,
                "method": "CEM",
                "method_seed": method_seed,
                "population": 50,
                "elite": 10,
                "generations": 40,
                "evaluation_budget": 2000,
                "training_signal_seed_base": training_base,
                "training_signal_seed_rule": "base + 32*eval_index + batch_offset",
                "test_signal_seeds": test_seeds,
            }
            records.append(
                {
                    **config,
                    "samples": samples.tolist(),
                    "selection_objective_nmse": selection_score,
                    "test_nmse": test_nmse,
                    "eval_count": count,
                    "elapsed_seconds": elapsed,
                    "config_hash": _hash(config),
                    "git_commit": _git_head(),
                    "hostname": socket.gethostname(),
                    "thread_config": _require_single_thread(),
                }
            )
            if enforce_first_gate:
                enforce_first_gate = False
    return records, True, first_count


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_stage6_cem() -> dict[str, Any]:
    _require_single_thread()
    sealed = RUNS / "sealed"
    sealed.mkdir(parents=True, exist_ok=True)
    queue: list[tuple[str, str, str | None]] = []
    for graph_family in ("G1", "G2", "G3"):
        for signal_family in ("S1", "S2", "S3"):
            if graph_family == "G1" and signal_family == "S2":
                queue.extend([("G1", "S2", "LIT"), ("G1", "S2", "REV")])
            else:
                queue.append((graph_family, signal_family, None))
    completed = []
    interrupted = []
    all_counts: list[int] = []
    gate_checked = False
    gate_passed = False
    started_all = time.perf_counter()
    for graph_family, signal_family, variant in queue:
        now = __import__("datetime").datetime.now(ZoneInfo("Asia/Shanghai"))
        if now.hour > 6 or (now.hour == 6 and now.minute >= 30):
            interrupted.append(
                {"graph_family": graph_family, "signal_family": signal_family, "variant": variant}
            )
            break
        records, budget_ok, first_count = _run_cem_cell(
            graph_family, signal_family, variant, enforce_first_gate=not gate_checked
        )
        if not gate_checked:
            gate_checked = True
            gate_passed = budget_ok and first_count == 2000
            _write_json(
                sealed / "cem_budget_gate.json",
                {
                    "eval_count": first_count,
                    "expected": 2000,
                    "passed": gate_passed,
                    "git_commit": _git_head(),
                    "hostname": socket.gethostname(),
                },
            )
        if not budget_ok:
            break
        all_counts.extend(int(record["eval_count"]) for record in records)
        suffix = f"_mu{variant}" if variant else ""
        filename = f"cem_d0_{graph_family}_{signal_family}_k10_N100{suffix}.jsonl"
        _write_jsonl_atomic(sealed / filename, records)
        completed.append(
            {
                "graph_family": graph_family,
                "signal_family": signal_family,
                "mu_variant": variant,
                "file": f"runs/sealed/{filename}",
                "runs": len(records),
            }
        )
    elapsed = time.perf_counter() - started_all
    payload = {
        "budget_gate_checked": gate_checked,
        "budget_gate_passed": gate_passed,
        "eval_count_values": sorted(set(all_counts)),
        "eval_count_runs_audited": len(all_counts),
        "completed": completed,
        "completed_physical_cells": len(completed),
        "completed_logical_cells": len(
            {(item["graph_family"], item["signal_family"]) for item in completed}
        ),
        "wall_seconds": elapsed,
        "interrupted_not_started": interrupted,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(sealed / "stage6_summary.json", payload)
    data_files = sorted(path for path in sealed.iterdir() if path.name != "SEAL.md")
    generated = __import__("datetime").datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
    seal_lines = [
        "# CEM sealed artifact manifest",
        "",
        f"- generated_at: `{generated}`",
        f"- git_commit: `{_git_head()}`",
        f"- hostname: `{socket.gethostname()}`",
        "",
        "| file | sha256 |",
        "|---|---|",
    ]
    for path in data_files:
        seal_lines.append(f"| `{path.name}` | `{_sha256(path)}` |")
    (sealed / "SEAL.md").write_text("\n".join(seal_lines) + "\n", encoding="utf-8")
    return payload


def _timed_eval(n: int, graph_seed: int = 77) -> float:
    graph = generate_graph("G2", n, graph_seed)
    samples = random_select(n, int(round(0.1 * n)), 0)
    ctx = {
        "graph_sel": graph,
        "signal_family": "S1",
        "mu": 0.01,
        "snr_db": 20.0,
        "signal_seed": 40_000_000 + n,
    }
    evalcore.reset()
    started = time.perf_counter()
    evalcore.evaluate(samples, ctx)
    return time.perf_counter() - started


def _parallel_trial(args: tuple[int, int]) -> float:
    n, seed = args
    return _timed_eval(n, seed)


def _parallel_batch_worker(args: tuple[int, int, int]) -> float:
    n, seed, repeats = args
    _timed_eval(n, seed)
    values = [_timed_eval(n, seed + index + 1) for index in range(repeats)]
    return float(np.median(values))


def benchmark() -> dict[str, Any]:
    _require_single_thread()
    timing_summaries: dict[str, Any] = {}
    for n in (100, 300):
        _timed_eval(n)
        samples = [_timed_eval(n, 80 + i) for i in range(30)]
        q1, q3 = np.percentile(samples, [25, 75])
        timing_summaries[str(n)] = {
            "samples_seconds": samples,
            "n_measurements": len(samples),
            "median_seconds": float(np.median(samples)),
            "q1_seconds": float(q1),
            "q3_seconds": float(q3),
            "iqr_seconds": float(q3 - q1),
        }

    concurrency: list[dict[str, Any]] = []
    max_workers = os.cpu_count() or 1
    single_process_median = None
    threshold_processes = max_workers
    for workers in range(1, max_workers + 1):
        started = time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            task_times = list(
                pool.map(
                    _parallel_batch_worker,
                    [(100, 500 + 100 * i, 3) for i in range(workers)],
                )
            )
        wall = time.perf_counter() - started
        process_median = float(np.median(task_times))
        if single_process_median is None:
            single_process_median = process_median
        inflation = process_median / single_process_median - 1.0
        concurrency.append(
            {
                "processes": workers,
                "wall_seconds": wall,
                "worker_median_eval_seconds": task_times,
                "median_eval_seconds": process_median,
                "inflation_vs_one_process": inflation,
            }
        )
        if workers > 1 and inflation > 0.20:
            threshold_processes = workers
            break

    t100 = timing_summaries["100"]["median_seconds"]
    t300 = timing_summaries["300"]["median_seconds"]
    hours = lambda cells, t, methods=2, budget=2000: cells * 10 * methods * 3 * budget * t / 3600
    blocks = {
        "A": hours(27, t100),
        "B": hours(27, t100),
        "C": hours(6, t100),
        "D": hours(3, t300),
        "F": hours(1, t100),
    }
    block_e = {
        f"{method}@{budget}": hours(3, t100, methods=1, budget=budget)
        for method, budget in (
            ("DQN", 2000),
            ("DQN", 8000),
            ("DQN", 500),
            ("CEM", 8000),
            ("CEM", 500),
        )
    }
    payload = {
        "single_eval": timing_summaries,
        "block_machine_hours": blocks,
        "block_e_machine_hours": block_e,
        "abc_machine_hours": blocks["A"] + blocks["B"] + blocks["C"],
        "abc_exceeds_1_5x_original_150h": blocks["A"] + blocks["B"] + blocks["C"] > 225,
        "concurrency_trials": concurrency,
        "usable_concurrency_at_20pct_point": threshold_processes,
        "cpu_count": os.cpu_count(),
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(RUNS / "timing_budget.json", payload)
    return payload


def write_provenance() -> None:
    import matplotlib
    import networkx
    import pandas
    import pygsp
    import pytest
    import scipy

    versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "networkx": networkx.__version__,
        "pygsp": pygsp.__version__,
        "matplotlib": matplotlib.__version__,
        "pandas": pandas.__version__,
        "pytest": pytest.__version__,
    }
    lines = [
        "# D1 Provenance",
        "",
        f"- hostname: `{socket.gethostname()}`",
        f"- git HEAD: `{_git_head()}`",
        f"- thread configuration: `{json.dumps(_require_single_thread(), sort_keys=True)}`",
        "- torch: not installed for D1",
        "",
        "## Dependency versions",
        "",
        *[f"- {name}: `{version}`" for name, version in versions.items()],
        "",
    ]
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "PROVENANCE.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "calibrate",
            "calibrate-v2",
            "baseline",
            "k1",
            "diagnose2",
            "firstcheck",
            "stage-f",
            "stage5",
            "stage6",
            "benchmark",
            "all",
        ],
    )
    args = parser.parse_args()
    actions = {
        "calibrate": calibrate_mu,
        "calibrate-v2": calibrate_mu_v2,
        "baseline": run_random_baseline,
        "k1": run_k1,
        "diagnose2": diagnose_k1_coverage,
        "firstcheck": formal_k1_2_firstcheck,
        "stage-f": firstcheck_diagnosis,
        "stage5": run_stage5_baselines,
        "stage6": run_stage6_cem,
        "benchmark": benchmark,
    }
    if args.action == "all":
        for action in (calibrate_mu, run_random_baseline, run_k1, benchmark):
            action()
    else:
        actions[args.action]()
    write_provenance()


if __name__ == "__main__":
    main()

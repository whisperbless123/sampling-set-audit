"""A-05 compliant Block A/B/C sweep with open baselines and sealed CEM."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import networkx as nx
import numpy as np

from src import evalcore
from src.graphs import generate_graph, rewire
from src.methods.b3a import select as b3a_select
from src.methods.b3b import select as b3b_select
from src.methods.b3c import select as b3c_select
from src.methods.cem import select as cem_select
from src.methods.degree import select as degree_select
from src.methods.random_sel import select as random_select
from src.runner import (
    A05_NO_RERUN_QUOTE,
    A05_PLATFORM_RULE_QUOTE,
    ROOT,
    RUNS,
    _git_head,
    _hash,
    _require_single_thread,
    _sha256,
    _signal_seeds,
    _write_json,
    _write_jsonl_atomic,
    write_provenance,
)
from src.signals import laplacian_eigh


WORKERS = 8


def block_cells(block: str) -> list[dict[str, Any]]:
    block = block.upper()
    cells: list[dict[str, Any]] = []
    if block == "A":
        for graph_family in ("G1", "G2", "G3"):
            for signal_family in ("S1", "S2", "S3"):
                for k_ratio in (0.05, 0.20):
                    cells.append(
                        {
                            "block": "A",
                            "graph_family": graph_family,
                            "model_sel": signal_family,
                            "model_eval": signal_family,
                            "drift": "D0",
                            "rho": None,
                            "k_ratio": k_ratio,
                        }
                    )
    elif block == "B":
        for graph_family in ("G1", "G2", "G3"):
            for signal_family in ("S1", "S2", "S3"):
                for rho in (0.05, 0.15, 0.30):
                    cells.append(
                        {
                            "block": "B",
                            "graph_family": graph_family,
                            "model_sel": signal_family,
                            "model_eval": signal_family,
                            "drift": "D-G",
                            "rho": rho,
                            "k_ratio": 0.10,
                        }
                    )
    elif block == "C":
        for model_sel in ("S1", "S2"):
            for graph_family in ("G1", "G2", "G3"):
                cells.append(
                    {
                        "block": "C",
                        "graph_family": graph_family,
                        "model_sel": model_sel,
                        "model_eval": "S3",
                        "drift": "D-S",
                        "rho": None,
                        "k_ratio": 0.10,
                    }
                )
    else:
        raise ValueError("block must be A, B, or C")
    return cells


def _cell_id(cell: dict[str, Any]) -> str:
    k_percent = int(round(100 * cell["k_ratio"]))
    if cell["block"] == "B":
        rho_percent = int(round(100 * cell["rho"]))
        return (
            f"B_{cell['graph_family']}_{cell['model_sel']}_DG_rho{rho_percent}_k{k_percent}"
        )
    if cell["block"] == "C":
        return f"C_{cell['graph_family']}_{cell['model_sel']}_to_{cell['model_eval']}_DS_k{k_percent}"
    return f"A_{cell['graph_family']}_{cell['model_sel']}_D0_k{k_percent}"


def _mu(graph_family: str, model_sel: str) -> float:
    calibration = json.loads(
        (RUNS / "mu_calibration_v2.json").read_text(encoding="utf-8")
    )
    if not calibration["frozen"] or calibration["status"] != "FROZEN":
        raise RuntimeError("A-05 mu table is not fully frozen")
    return float(calibration["combinations"][f"{graph_family}_{model_sel}"]["value"])


def _graphs(cell: dict[str, Any], graph_seed: int) -> tuple[nx.Graph, nx.Graph, int | None]:
    graph_sel = generate_graph(cell["graph_family"], 100, graph_seed)
    if cell["drift"] != "D-G":
        return graph_sel, graph_sel, None
    rho_index = {0.05: 0, 0.15: 1, 0.30: 2}[cell["rho"]]
    rewire_seed = 500 + 10 * rho_index + graph_seed
    return graph_sel, rewire(graph_sel, float(cell["rho"]), rewire_seed), rewire_seed


def _base_config(
    cell: dict[str, Any], graph_seed: int, rewire_seed: int | None, mu: float
) -> dict[str, Any]:
    return {
        **cell,
        "cell_id": _cell_id(cell),
        "n": 100,
        "k": int(round(100 * cell["k_ratio"])),
        "mu": mu,
        "graph_seed": graph_seed,
        "rewire_seed": rewire_seed,
        "snr_db": 20.0,
    }


def _baseline_graph_worker(args: tuple[dict[str, Any], int]) -> list[dict[str, Any]]:
    cell, graph_seed = args
    _require_single_thread()
    graph_sel, graph_eval, rewire_seed = _graphs(cell, graph_seed)
    eigenvalues, basis = laplacian_eigh(graph_sel)
    laplacian = nx.laplacian_matrix(graph_sel, nodelist=range(100)).toarray().astype(float)
    mu = _mu(cell["graph_family"], cell["model_sel"])
    k = int(round(100 * cell["k_ratio"]))
    sigma2 = float(np.mean(1.0 / (eigenvalues + 1e-2)) / 100.0)
    selections = {
        "Degree": degree_select(graph_sel, k),
        "B3a": b3a_select(basis, 10, k),
        "B3b": b3b_select(laplacian, mu, k),
        "B3c": b3c_select(laplacian, mu, sigma2, k),
    }
    signal_seeds = _signal_seeds(graph_seed, 200, calibration=False)
    context = {
        "graph_sel": graph_sel,
        "graph_eval": graph_eval,
        "signal_family": cell["model_eval"],
        "mu": mu,
        "snr_db": 20.0,
    }
    method_items = [
        ("Random", seed, random_select(100, k, seed)) for seed in range(3)
    ] + [(name, None, samples) for name, samples in selections.items()]
    base = _base_config(cell, graph_seed, rewire_seed, mu)
    head = _git_head()
    records = []
    for method, method_seed, samples in method_items:
        config = {
            **base,
            "method": method,
            "method_seed": method_seed,
            "signal_seeds": signal_seeds,
        }
        evalcore.reset()
        started = time.perf_counter()
        nmse = evalcore.score_test_set(samples, context, signal_seeds)
        records.append(
            {
                **config,
                "samples": samples.tolist(),
                "nmse": nmse,
                "eval_count": evalcore.eval_count(),
                "elapsed_seconds": time.perf_counter() - started,
                "config_hash": _hash(config),
                "git_commit": head,
                "hostname": socket.gethostname(),
                "thread_config": _require_single_thread(),
            }
        )
    return records


def _training_seed_base(cell: dict[str, Any], graph_seed: int, method_seed: int) -> int:
    identity = f"{_cell_id(cell)}:{graph_seed}:{method_seed}"
    return 1_000_000_000 + int(hashlib.sha256(identity.encode()).hexdigest()[:12], 16)


def _cem_worker(args: tuple[dict[str, Any], int, int]) -> dict[str, Any]:
    cell, graph_seed, method_seed = args
    _require_single_thread()
    graph_sel, graph_eval, rewire_seed = _graphs(cell, graph_seed)
    mu = _mu(cell["graph_family"], cell["model_sel"])
    k = int(round(100 * cell["k_ratio"]))
    training_base = _training_seed_base(cell, graph_seed, method_seed)
    training_context = {
        "graph_sel": graph_sel,
        "signal_family": cell["model_sel"],
        "mu": mu,
        "snr_db": 20.0,
    }
    evalcore.reset()

    def objective(samples: np.ndarray) -> float:
        call_index = evalcore.eval_count()
        seeds = [training_base + 32 * call_index + offset for offset in range(32)]
        return evalcore.evaluate(samples, {**training_context, "signal_seeds": seeds})

    started = time.perf_counter()
    samples, selection_score = cem_select(100, k, method_seed, objective)
    count = evalcore.eval_count()
    test_seeds = _signal_seeds(graph_seed, 200, calibration=False)
    test_context = {
        "graph_sel": graph_sel,
        "graph_eval": graph_eval,
        "signal_family": cell["model_eval"],
        "mu": mu,
        "snr_db": 20.0,
    }
    test_nmse = evalcore.score_test_set(samples, test_context, test_seeds)
    base = _base_config(cell, graph_seed, rewire_seed, mu)
    config = {
        **base,
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
    return {
        **config,
        "samples": samples.tolist(),
        "selection_objective_nmse": selection_score,
        "test_nmse": test_nmse,
        "eval_count": count,
        "elapsed_seconds": time.perf_counter() - started,
        "config_hash": _hash(config),
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }


def _baseline_flags(cell_id: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flags = []
    for record in records:
        if not np.isfinite(record["nmse"]) or record["nmse"] > 10:
            flags.append({"flag": "a", "cell": cell_id, "run": record["config_hash"]})
        if record["eval_count"] != 0:
            flags.append({"flag": "c", "cell": cell_id, "run": record["config_hash"]})
    seed_means = [
        float(
            np.mean(
                [
                    row["nmse"]
                    for row in records
                    if row["method"] == "Random" and row["method_seed"] == seed
                ]
            )
        )
        for seed in range(3)
    ]
    mean = float(np.mean(seed_means))
    sd = float(np.std(seed_means, ddof=1))
    if sd > 0.5 * mean:
        flags.append(
            {
                "flag": "b",
                "cell": cell_id,
                "random_seed_means": seed_means,
                "random_mean": mean,
                "random_sd": sd,
            }
        )
    return flags


def _d0_reuse_paths() -> list[Path]:
    paths = []
    for graph_family in ("G1", "G2", "G3"):
        for signal_family in ("S1", "S2", "S3"):
            suffix = "_muREV" if (graph_family, signal_family) == ("G1", "S2") else ""
            paths.append(RUNS / f"d0_{graph_family}_{signal_family}_k10_N100{suffix}.jsonl")
            paths.append(
                RUNS
                / "sealed"
                / f"cem_d0_{graph_family}_{signal_family}_k10_N100{suffix}.jsonl"
            )
    return paths


def _fingerprints(paths: list[Path]) -> dict[str, str]:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"required reused D0 files missing: {missing}")
    return {str(path.relative_to(ROOT)): _sha256(path) for path in paths}


def _write_seal_manifest() -> None:
    sealed = RUNS / "sealed"
    files = sorted(path for path in sealed.iterdir() if path.name != "SEAL.md")
    lines = [
        "# CEM sealed artifact manifest",
        "",
        f"- generated_at: `{datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()}`",
        f"- git_commit: `{_git_head()}`",
        f"- hostname: `{socket.gethostname()}`",
        "",
        "| file | sha256 |",
        "|---|---|",
    ]
    lines.extend(f"| `{path.name}` | `{_sha256(path)}` |" for path in files)
    (sealed / "SEAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_block(block: str) -> dict[str, Any]:
    _require_single_thread()
    block = block.upper()
    cells = block_cells(block)
    expected_counts = {"A": 18, "B": 27, "C": 6}
    if len(cells) != expected_counts[block]:
        raise RuntimeError(f"cell count mismatch for Block {block}")
    summary_path = RUNS / f"block_{block}_summary.json"
    if summary_path.exists():
        raise FileExistsError(f"refusing to rerun completed Block {block}")
    reused_paths = _d0_reuse_paths()
    before = _fingerprints(reused_paths)
    completed = []
    flags: list[dict[str, Any]] = []
    cem_gate_passed = True
    started = time.perf_counter()
    compliance_checks = [
        {
            "kind": "start",
            "time": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            "a05_platform_rule_quote": A05_PLATFORM_RULE_QUOTE,
            "a05_no_rerun_quote": A05_NO_RERUN_QUOTE,
            "threads": _require_single_thread(),
        }
    ]
    last_check = started
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for cell in cells:
            cell_id = _cell_id(cell)
            baseline_path = RUNS / f"{cell_id}.jsonl"
            cem_path = RUNS / "sealed" / f"cem_{cell_id}.jsonl"
            if baseline_path.exists() or cem_path.exists():
                raise FileExistsError(f"refusing to overwrite cell {cell_id}")
            baseline_batches = list(
                pool.map(_baseline_graph_worker, [(cell, seed) for seed in range(10)])
            )
            baseline_records = [row for batch in baseline_batches for row in batch]
            cell_flags = _baseline_flags(cell_id, baseline_records)
            _write_jsonl_atomic(baseline_path, baseline_records)
            flags.extend(cell_flags)
            if cell_flags:
                break
            cem_records = list(
                pool.map(
                    _cem_worker,
                    [
                        (cell, graph_seed, method_seed)
                        for graph_seed in range(10)
                        for method_seed in range(3)
                    ],
                )
            )
            counts = sorted({int(row["eval_count"]) for row in cem_records})
            if counts != [2000]:
                cem_gate_passed = False
                break
            _write_jsonl_atomic(cem_path, cem_records)
            completed.append(
                {
                    "cell_id": cell_id,
                    "baseline_file": str(baseline_path.relative_to(ROOT)),
                    "baseline_runs": len(baseline_records),
                    "cem_file": str(cem_path.relative_to(ROOT)),
                    "cem_runs": len(cem_records),
                    "cem_eval_count_values": counts,
                    "cem_sha256": _sha256(cem_path),
                }
            )
            if time.perf_counter() - last_check >= 1800:
                current = _fingerprints(reused_paths)
                if current != before:
                    raise RuntimeError("forbidden D0/k10 reuse files changed")
                compliance_checks.append(
                    {
                        "kind": "30-minute",
                        "time": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
                        "threads": _require_single_thread(),
                        "d0_reuse_unchanged": True,
                        "dqn_implemented": (ROOT / "src" / "methods" / "dqn.py").exists(),
                    }
                )
                last_check = time.perf_counter()
    after = _fingerprints(reused_paths)
    if after != before:
        raise RuntimeError("forbidden D0/k10 reuse files changed")
    compliance_checks.append(
        {
            "kind": "final",
            "time": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            "threads": _require_single_thread(),
            "d0_reuse_unchanged": True,
            "dqn_implemented": (ROOT / "src" / "methods" / "dqn.py").exists(),
        }
    )
    payload = {
        "block": block,
        "expected_new_cells": expected_counts[block],
        "completed_new_cells": len(completed),
        "reused_d0_k10_cells": 9 if block == "A" else 0,
        "completed": completed,
        "flags": flags,
        "diagnostic_gate_passed": not flags,
        "cem_budget_gate_passed": cem_gate_passed,
        "wall_seconds": time.perf_counter() - started,
        "d0_k10_reuse_fingerprints": before if block == "A" else {},
        "compliance_checks": compliance_checks,
        "git_commit": _git_head(),
        "hostname": socket.gethostname(),
        "thread_config": _require_single_thread(),
    }
    _write_json(summary_path, payload)
    _write_seal_manifest()
    write_provenance()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("block", choices=["A", "B", "C", "a", "b", "c"])
    args = parser.parse_args()
    run_block(args.block)


if __name__ == "__main__":
    main()


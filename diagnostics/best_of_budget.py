"""A-24#2 best-of-2000 Random diagnostic with sealed performance output."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from src import evalcore
from src.graphs import generate_graph
from src.runner import _signal_seeds


ROOT = Path(__file__).resolve().parents[1]
SEALED_OUTPUT = ROOT / "runs" / "sealed" / "best_of_budget_A24_2.jsonl"
OPEN_OUTPUT = ROOT / "runs" / "best_of_budget.json"
EVALUATION_BUDGET = 2000
WORKERS = min(8, os.cpu_count() or 1)


def require_environment() -> None:
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        if os.environ.get(key) != "1":
            raise RuntimeError(f"{key} must be 1")


def frozen_mu(graph_family: str, signal_family: str) -> float:
    payload = json.loads(
        (ROOT / "runs" / "mu_calibration_v2.json").read_text(encoding="utf-8")
    )
    return float(payload["combinations"][f"{graph_family}_{signal_family}"]["value"])


def integer_seed(identity: str, namespace: int) -> int:
    value = int(hashlib.sha256(identity.encode()).hexdigest()[:12], 16)
    return namespace + value


def worker(task: tuple[str, str, int, int]) -> dict[str, object]:
    require_environment()
    graph_family, signal_family, graph_seed, method_seed = task
    graph = generate_graph(graph_family, 100, graph_seed)
    mu = frozen_mu(graph_family, signal_family)
    cell = f"{graph_family}_{signal_family}_D0_k10_N100"
    identity = f"{cell}:{graph_seed}:{method_seed}:A24-2"
    candidate_seed = integer_seed(identity, 2_420_000_000)
    signal_seed_base = integer_seed(identity, 2_430_000_000)
    rng = np.random.default_rng(candidate_seed)
    context = {
        "graph_sel": graph,
        "signal_family": signal_family,
        "mu": mu,
        "snr_db": 20.0,
    }
    evalcore.reset()
    best_samples: np.ndarray | None = None
    best_score = float("inf")
    started = time.perf_counter()
    for _ in range(EVALUATION_BUDGET):
        samples = np.sort(rng.choice(100, size=10, replace=False))
        call_index = evalcore.eval_count()
        seeds = [signal_seed_base + 32 * call_index + offset for offset in range(32)]
        score = evalcore.evaluate(samples, {**context, "signal_seeds": seeds})
        if score < best_score:
            best_score = float(score)
            best_samples = samples.copy()
    count = evalcore.eval_count()
    if count != EVALUATION_BUDGET or best_samples is None:
        raise RuntimeError(f"eval_count={count}; expected={EVALUATION_BUDGET}")
    test_seeds = _signal_seeds(graph_seed, 200, calibration=False)
    test_nmse = evalcore.score_test_set(best_samples, context, test_seeds)
    elapsed = time.perf_counter() - started
    return {
        "cell": cell,
        "graph_family": graph_family,
        "signal_family": signal_family,
        "graph_seed": graph_seed,
        "method": "BestOfBudgetRandom",
        "method_seed": method_seed,
        "candidate_seed": candidate_seed,
        "training_signal_seed_base": signal_seed_base,
        "training_signal_seed_rule": "base + 32*eval_index + batch_offset",
        "evaluation_budget": EVALUATION_BUDGET,
        "eval_count": count,
        "samples": best_samples.tolist(),
        "selection_objective_nmse": best_score,
        "test_signal_seeds": test_seeds,
        "test_nmse": float(test_nmse),
        "elapsed_seconds": elapsed,
        "thread_config": {
            key: os.environ[key]
            for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")
        },
    }


def main() -> None:
    require_environment()
    if SEALED_OUTPUT.exists() or OPEN_OUTPUT.exists():
        raise FileExistsError("refusing to overwrite best-of-budget output")
    tasks = [
        (graph_family, signal_family, graph_seed, method_seed)
        for graph_family in ("G1", "G2", "G3")
        for signal_family in ("S1", "S2", "S3")
        for graph_seed in range(10)
        for method_seed in range(3)
    ]
    started = time.perf_counter()
    rows: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(worker, task) for task in tasks]
        for index, future in enumerate(as_completed(futures), 1):
            rows.append(future.result())
            if index % 10 == 0 or index == len(futures):
                print(
                    json.dumps(
                        {
                            "completed": index,
                            "total": len(futures),
                            "elapsed_seconds": time.perf_counter() - started,
                        }
                    ),
                    flush=True,
                )
    rows.sort(
        key=lambda row: (
            row["graph_family"],
            row["signal_family"],
            int(row["graph_seed"]),
            int(row["method_seed"]),
        )
    )
    if len(rows) != 270 or any(
        int(row["eval_count"]) != EVALUATION_BUDGET for row in rows
    ):
        raise RuntimeError("best-of-budget completeness or accounting failure")
    with SEALED_OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")

    open_rows = [
        {
            "cell": row["cell"],
            "graph_seed": row["graph_seed"],
            "method_seed": row["method_seed"],
            "evaluation_budget": row["evaluation_budget"],
            "eval_count": row["eval_count"],
            "elapsed_seconds": row["elapsed_seconds"],
        }
        for row in rows
    ]
    payload = {
        "authorization": "A-24 item 2",
        "scope": "D0 nine cells; k=10%; 10 graphs x 3 method seeds",
        "method": "best of 2000 uniformly sampled candidate sets",
        "performance_location": "runs/sealed/best_of_budget_A24_2.jsonl",
        "performance_fields_exposed": False,
        "run_count": len(open_rows),
        "all_eval_counts_exact": True,
        "rows": open_rows,
        "total_wall_seconds": time.perf_counter() - started,
        "worker_processes": WORKERS,
        "git_commit_at_generation": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT
        )
        .decode()
        .strip(),
    }
    OPEN_OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "sealed_output": str(SEALED_OUTPUT.relative_to(ROOT)),
                "open_output": str(OPEN_OUTPUT.relative_to(ROOT)),
                "runs": len(rows),
                "all_eval_counts_exact": True,
                "total_wall_seconds": payload["total_wall_seconds"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

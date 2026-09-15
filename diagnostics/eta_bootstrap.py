"""A-27#2 eta post-processing under both literal random-risk readings."""

from __future__ import annotations

import json
import math
import os
import subprocess
from pathlib import Path

import numpy as np

from diagnostics.oracle_risk import analytic_risk, matrices


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "runs" / "oracle_risk_diagnostic.json"
OUTPUT = ROOT / "runs" / "eta_bootstrap.json"
MC_SUBSETS = 2_000
BOOTSTRAP_REPLICATES = 10_000
MC_SEED_BASE = 28_200
BOOTSTRAP_SEED_BASE = 28_700
TRANSLATED_BOUND = 0.021


def require_environment() -> None:
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        if os.environ.get(key) != "1":
            raise RuntimeError(f"{key} must be 1")


def ratio(random_risk: float, oracle_risk: float) -> float:
    if random_risk <= 0:
        raise ValueError("random mean risk must be positive")
    return (random_risk - oracle_risk) / random_risk


def bootstrap_interval(
    random_values: np.ndarray,
    oracle_values: np.ndarray,
    seed: int,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    n_graphs = len(random_values)
    estimates = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
    for index in range(BOOTSTRAP_REPLICATES):
        picked = rng.integers(0, n_graphs, size=n_graphs)
        estimates[index] = ratio(
            float(np.mean(random_values[picked])),
            float(np.mean(oracle_values[picked])),
        )
    lower, upper = np.percentile(estimates, [2.5, 97.5])
    return {
        "seed": seed,
        "replicates": BOOTSTRAP_REPLICATES,
        "unit": "graph",
        "resampling": "with replacement within cell",
        "percentile_interval": [float(lower), float(upper)],
    }


def range_distance(value: float, low: float, high: float) -> float:
    if low <= value <= high:
        return 0.0
    return min(abs(value - low), abs(value - high))


def main() -> None:
    require_environment()
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    cells_out: list[dict[str, object]] = []
    all_oracle: list[float] = []
    all_d1: list[float] = []
    all_d2: list[float] = []
    materially_different_graphs = 0

    for cell_index, cell in enumerate(source["cells"]):
        family = str(cell["cell"]).split("_")[0]
        mu = float(cell["mu"])
        graph_rows: list[dict[str, object]] = []
        for graph_index, graph in enumerate(cell["graphs"]):
            graph_seed = int(graph["graph_seed"])
            oracle = float(graph["oracle_risk"])
            random_runs = graph["methods"]["Random"]["runs"]
            if len(random_runs) != 3 or any("risk" not in run for run in random_runs):
                raise RuntimeError(f"{cell['cell']} graph {graph_seed}: Random R(S) missing")
            d1_runs = [float(run["risk"]) for run in random_runs]
            d1_mean = float(np.mean(d1_runs))

            data = matrices(family, graph_seed)
            mc_seed = MC_SEED_BASE + 100 * cell_index + graph_index
            rng = np.random.default_rng(mc_seed)
            d2_values = np.empty(MC_SUBSETS, dtype=float)
            for draw in range(MC_SUBSETS):
                samples = rng.choice(100, 10, replace=False)
                d2_values[draw] = analytic_risk(samples, mu, data)
            d2_mean = float(np.mean(d2_values))
            d2_se = float(np.std(d2_values, ddof=1) / math.sqrt(MC_SUBSETS))
            d2_mc95 = [d2_mean - 1.96 * d2_se, d2_mean + 1.96 * d2_se]
            d1_outside_d2_mc95 = not (d2_mc95[0] <= d1_mean <= d2_mc95[1])
            materially_different_graphs += int(d1_outside_d2_mc95)
            graph_rows.append(
                {
                    "graph_seed": graph_seed,
                    "oracle_risk": oracle,
                    "D1": {
                        "random_run_risks": d1_runs,
                        "random_mean_risk": d1_mean,
                        "absolute_gap": d1_mean - oracle,
                        "eta": ratio(d1_mean, oracle),
                    },
                    "D2": {
                        "mc_seed": mc_seed,
                        "uniform_k_subsets": MC_SUBSETS,
                        "random_mean_risk": d2_mean,
                        "standard_error": d2_se,
                        "mc_mean_95_interval": d2_mc95,
                        "absolute_gap": d2_mean - oracle,
                        "eta": ratio(d2_mean, oracle),
                    },
                    "d1_random_mean_outside_d2_mc_mean_95_interval": d1_outside_d2_mc95,
                }
            )

        oracle_values = np.asarray([row["oracle_risk"] for row in graph_rows], dtype=float)
        d1_values = np.asarray([row["D1"]["random_mean_risk"] for row in graph_rows], dtype=float)
        d2_values = np.asarray([row["D2"]["random_mean_risk"] for row in graph_rows], dtype=float)
        cell_out: dict[str, object] = {
            "cell": cell["cell"],
            "graphs": graph_rows,
            "aggregate": {
                "oracle_mean_risk": float(np.mean(oracle_values)),
                "D1": {
                    "random_mean_risk": float(np.mean(d1_values)),
                    "absolute_gap": float(np.mean(d1_values) - np.mean(oracle_values)),
                    "eta": ratio(float(np.mean(d1_values)), float(np.mean(oracle_values))),
                    "bootstrap": bootstrap_interval(
                        d1_values, oracle_values, BOOTSTRAP_SEED_BASE + 2 * cell_index
                    ),
                },
                "D2": {
                    "random_mean_risk": float(np.mean(d2_values)),
                    "absolute_gap": float(np.mean(d2_values) - np.mean(oracle_values)),
                    "eta": ratio(float(np.mean(d2_values)), float(np.mean(oracle_values))),
                    "bootstrap": bootstrap_interval(
                        d2_values, oracle_values, BOOTSTRAP_SEED_BASE + 2 * cell_index + 1
                    ),
                },
            },
        }
        cells_out.append(cell_out)
        all_oracle.extend(oracle_values.tolist())
        all_d1.extend(d1_values.tolist())
        all_d2.extend(d2_values.tolist())

    oracle_all = np.asarray(all_oracle)
    d1_all = np.asarray(all_d1)
    d2_all = np.asarray(all_d2)
    d1_cell_eta = [float(cell["aggregate"]["D1"]["eta"]) for cell in cells_out]
    d2_cell_eta = [float(cell["aggregate"]["D2"]["eta"]) for cell in cells_out]
    d1_range = [min(d1_cell_eta), max(d1_cell_eta)]
    d2_range = [min(d2_cell_eta), max(d2_cell_eta)]
    d1_supports_bound = d1_range[1] <= TRANSLATED_BOUND
    d2_supports_bound = d2_range[1] <= TRANSLATED_BOUND
    if d1_supports_bound and d2_supports_bound:
        fidelity = "相符"
    elif d1_supports_bound or d2_supports_bound:
        fidelity = "部分相符"
    else:
        fidelity = "不符"
    d1_distance = range_distance(TRANSLATED_BOUND, *d1_range)
    d2_distance = range_distance(TRANSLATED_BOUND, *d2_range)
    closer = "D1" if d1_distance < d2_distance else "D2" if d2_distance < d1_distance else "等距"

    payload = {
        "authorization": "A-27 item 2",
        "input": "runs/oracle_risk_diagnostic.json",
        "eta_definition": "(random_mean_risk - oracle_risk) / random_mean_risk",
        "D1_definition": "mean R(S) of the three realized Random method seeds",
        "D2_definition": "Monte Carlo expectation of R(S) over uniform k-subsets",
        "D2_uniform_k_subset_draws_per_cell_graph": MC_SUBSETS,
        "bootstrap_replicates_per_cell_reading": BOOTSTRAP_REPLICATES,
        "cells": cells_out,
        "pooled_30_graphs": {
            "oracle_mean_risk": float(np.mean(oracle_all)),
            "D1": {
                "random_mean_risk": float(np.mean(d1_all)),
                "absolute_gap": float(np.mean(d1_all) - np.mean(oracle_all)),
                "eta": ratio(float(np.mean(d1_all)), float(np.mean(oracle_all))),
            },
            "D2": {
                "random_mean_risk": float(np.mean(d2_all)),
                "absolute_gap": float(np.mean(d2_all) - np.mean(oracle_all)),
                "eta": ratio(float(np.mean(d2_all)), float(np.mean(oracle_all))),
            },
        },
        "ETA_DENOM_SPLIT": materially_different_graphs > 0,
        "ETA_DENOM_SPLIT_rule": (
            "true iff at least one graph's D1 mean lies outside the D2 Monte Carlo "
            "mean plus/minus 1.96 standard errors"
        ),
        "materially_different_graph_count": materially_different_graphs,
        "paraphrase_fidelity": {
            "translated_bound": TRANSLATED_BOUND,
            "D1_cell_eta_range": d1_range,
            "D2_cell_eta_range": d2_range,
            "translated_value_in_D1_cell_range": d1_range[0] <= TRANSLATED_BOUND <= d1_range[1],
            "translated_value_in_D2_cell_range": d2_range[0] <= TRANSLATED_BOUND <= d2_range[1],
            "D1_supports_all_cells_at_or_below_bound": d1_supports_bound,
            "D2_supports_all_cells_at_or_below_bound": d2_supports_bound,
            "closer_reading_by_distance_to_cell_range": closer,
            "PARAPHRASE_FIDELITY_ETA": fidelity,
        },
        "best_deployment_oracle_gaps_from_existing_report": [0.0249, 0.0578, 0.0965],
        "best_deployment_gap_note": (
            "These are best-deployment R(S) minus oracle R(S), not eta numerators or denominators."
        ),
        "no_new_selection_or_reconstruction_experiment": True,
        "git_commit_at_generation": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT
        ).decode().strip(),
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
                "cell_eta_D1": d1_cell_eta,
                "cell_eta_D2": d2_cell_eta,
                "pooled_eta_D1": payload["pooled_30_graphs"]["D1"]["eta"],
                "pooled_eta_D2": payload["pooled_30_graphs"]["D2"]["eta"],
                "ETA_DENOM_SPLIT": payload["ETA_DENOM_SPLIT"],
                "PARAPHRASE_FIDELITY_ETA": fidelity,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

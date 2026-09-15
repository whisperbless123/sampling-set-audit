# Supplementary and reproducibility materials

Supplementary and reproducibility materials for *When Is Sampling-Set Choice Resolvable? A Budget-Audited Controlled Study on Graph Signals* (ICASSP).

## Where to start

Use [NUMBERS_PROVENANCE.md](NUMBERS_PROVENANCE.md) to trace each reported number to a released record. The frozen design is in [protocol/D0_experiment_protocol.md](protocol/D0_experiment_protocol.md), and the implementation is in [src/](src/).

## Contents

| Ref | Title | Path |
|---|---|---|
| S1 | Per-work literature facts | [supp/literature_facts.md](supp/literature_facts.md) |
| S2 | 60-cell design table | [supp/design_table.md](supp/design_table.md) |
| S3 | Block D redraw counts | [runs/block_D_summary.json](runs/block_D_summary.json) |
| S4 | Separation threshold formula and example | [supp/delta_table.md](supp/delta_table.md) |
| S5 | Preregistered robustness exits | [runs/robustness_exits.md](runs/robustness_exits.md) |
| S6 | Threshold sensitivity | [supp/threshold_sensitivity.md](supp/threshold_sensitivity.md) |
| S7 | Best-of-budget control | [supp/best_of_budget.md](supp/best_of_budget.md) |
| S8 | DQN descriptive comparison | [supp/dqn_descriptive_comparison.md](supp/dqn_descriptive_comparison.md) |
| S9 | Mu sensitivity strata | [supp/mu_sensitivity_strata.md](supp/mu_sensitivity_strata.md) |

## Reproducing

Orchestration scripts are not included.

The commands below were executed in Windows PowerShell. Use Python 3.13.5 and a project-local `.venv` with the exact pins in [requirements.txt](requirements.txt). Run from the repository root in a separate working copy: these commands generate or replace records. Use the released calibration in `runs/mu_calibration_v2.json`; no calibration command is needed here.

### Firstcheck

```powershell
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.runner firstcheck
```

Output: `runs/k1_2_firstcheck.json`.

### Baseline and timing

```powershell
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.runner baseline; .\.venv\Scripts\python.exe -m src.runner benchmark
```

Outputs: `runs/random_G2_S1_D0_k10_N100.jsonl` and `runs/timing_budget.json`.

### D0 baseline methods

```powershell
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.runner stage5
```

Outputs: `runs/stage5_summary.json` and the per-cell `runs/d0_*.jsonl` records.

### D0 CEM

```powershell
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.runner stage6
```

Outputs: `runs/sealed/stage6_summary.json` and `runs/sealed/cem_d0_*.jsonl`.

### Blocks A, B and C

```powershell
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.block_abc A
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.block_abc B
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; .\.venv\Scripts\python.exe -m src.block_abc C
```

Outputs: `runs/block_A_summary.json`, `runs/block_B_summary.json`, `runs/block_C_summary.json`, and their per-cell records in `runs/` and `runs/sealed/`.

Only firstcheck was re-verified in a clean environment for this release. Its result rows match the released record; the isolated run has a different commit identifier. The other commands are historical execution records, not a claim that every stage has been re-verified. Runner commands also write `runs/PROVENANCE.md` in the working copy.

reproduces stage firstcheck

## Protocol

The frozen experimental protocol is in `protocol/D0_experiment_protocol.md`.
Decision thresholds were fixed before the results they govern were computed.

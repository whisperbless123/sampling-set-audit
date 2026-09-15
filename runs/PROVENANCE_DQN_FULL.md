# DQN full-scope provenance

- generated_at: `2026-09-05T01:33:09.971968+08:00`
- execution_commit: `24713b48d5dd026bf3102d1f1b7f3e65ae2b790d`
- hostname: `DESKTOP-O16RHSN`
- platform: `Windows-11-10.0.26200-SP0`
- Python: `3.13.5`
- torch: `2.14.0+cpu`
- CUDA build / available: `None` / `False`
- device: `cpu`; deterministic algorithms enabled; cuDNN deterministic=true, benchmark=false
- workers: `8`; OMP/MKL/OpenBLAS threads per worker: `1/1/1`
- total runs: `450`; wall elapsed: `4410.591239 s`
- E=500: `90` runs, eval_count unique `[500]`
- E=2000: `270` runs, eval_count unique `[2000]`
- E=8000: `90` runs, eval_count unique `[8000]`
- Block E E=2000: directly references the three diagonal D0 files; no rerun

## Sealed files

- `runs/sealed/dqn_E_G1_S1_D0_k10_N100_E500.jsonl`
- `runs/sealed/dqn_E_G1_S1_D0_k10_N100_E8000.jsonl`
- `runs/sealed/dqn_E_G2_S2_D0_k10_N100_E500.jsonl`
- `runs/sealed/dqn_E_G2_S2_D0_k10_N100_E8000.jsonl`
- `runs/sealed/dqn_E_G3_S3_D0_k10_N100_E500.jsonl`
- `runs/sealed/dqn_E_G3_S3_D0_k10_N100_E8000.jsonl`
- `runs/sealed/dqn_d0_G1_S1_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G1_S2_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G1_S3_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G2_S1_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G2_S2_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G2_S3_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G3_S1_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G3_S2_k10_N100.jsonl`
- `runs/sealed/dqn_d0_G3_S3_k10_N100.jsonl`

## pip freeze

```text
colorama==0.4.6
contourpy==1.3.3
cycler==0.12.1
filelock==3.32.5
fonttools==4.64.0
fsspec==2026.7.0
iniconfig==2.3.0
Jinja2==3.1.6
kiwisolver==1.5.1
MarkupSafe==3.0.3
matplotlib==3.11.1
mpmath==1.3.0
networkx==3.6.1
numpy==2.5.2
packaging==26.3
pandas==3.0.5
pillow==12.3.0
pluggy==1.6.0
psutil==7.2.2
Pygments==2.21.0
PyGSP==0.6.1
pyparsing==3.3.2
pytest==9.1.1
python-dateutil==2.9.0.post0
scipy==1.18.1
setuptools==84.0.0
six==1.17.0
sympy==1.14.0
torch==2.14.0
typing_extensions==4.16.0
tzdata==2026.3
```

"""B3a exact E-optimal greedy sampling-set selection."""

from __future__ import annotations

import numpy as np


def select(eigenvectors: np.ndarray, r: int, k: int) -> np.ndarray:
    basis = np.asarray(eigenvectors, dtype=float)[:, :r]
    chosen: list[int] = []
    remaining = set(range(basis.shape[0]))
    for _ in range(k):
        best_node = min(remaining)
        best_value = -np.inf
        for node in sorted(remaining):
            candidate = chosen + [node]
            sigma_min = float(np.linalg.svd(basis[candidate, :], compute_uv=False)[-1])
            if sigma_min > best_value:
                best_value = sigma_min
                best_node = node
        chosen.append(best_node)
        remaining.remove(best_node)
    return np.sort(np.asarray(chosen, dtype=int))


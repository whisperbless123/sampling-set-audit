"""B3c exact A-optimal greedy baseline with Sherman-Morrison updates."""

from __future__ import annotations

import numpy as np


def select(laplacian: np.ndarray, mu: float, sigma2: float, k: int) -> np.ndarray:
    precision = float(mu) * np.asarray(laplacian, dtype=float)
    n = precision.shape[0]
    remaining = set(range(n))
    chosen: list[int] = []

    best_node = 0
    best_trace = np.inf
    best_inverse = None
    for node in range(n):
        candidate = precision.copy()
        candidate[node, node] += 1.0 / sigma2
        try:
            inverse = np.linalg.inv(candidate)
        except np.linalg.LinAlgError:
            continue
        trace = float(np.trace(inverse))
        if trace < best_trace:
            best_trace = trace
            best_node = node
            best_inverse = inverse
    if best_inverse is None:
        raise np.linalg.LinAlgError("A-optimal precision remains singular after one sample")
    chosen.append(best_node)
    remaining.remove(best_node)
    inverse = best_inverse

    while len(chosen) < k:
        best_node = min(remaining)
        best_reduction = -np.inf
        for node in sorted(remaining):
            column = inverse[:, node]
            reduction = float(column @ column / (sigma2 + inverse[node, node]))
            if reduction > best_reduction:
                best_reduction = reduction
                best_node = node
        column = inverse[:, best_node].copy()
        inverse -= np.outer(column, column) / (sigma2 + inverse[best_node, best_node])
        chosen.append(best_node)
        remaining.remove(best_node)
    return np.sort(np.asarray(chosen, dtype=int))


"""B3b exact lambda-min greedy baseline matched to Laplacian reconstruction."""

from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh


def select(laplacian: np.ndarray, mu: float, k: int) -> np.ndarray:
    matrix = float(mu) * np.asarray(laplacian, dtype=float)
    sparse_matrix = sparse.csr_matrix(matrix) if matrix.shape[0] >= 300 else None
    chosen: list[int] = []
    remaining = set(range(matrix.shape[0]))
    for _ in range(k):
        best_node = min(remaining)
        best_value = -np.inf
        for node in sorted(remaining):
            indices = chosen + [node]
            if matrix.shape[0] >= 300:
                diagonal = np.zeros(matrix.shape[0], dtype=float)
                diagonal[indices] = 1.0
                candidate = sparse_matrix + sparse.diags(diagonal, format="csr")
                value = float(
                    eigsh(
                        candidate,
                        k=1,
                        which="SA",
                        return_eigenvectors=False,
                        v0=np.linspace(1.0, 2.0, matrix.shape[0]),
                        tol=0.0,
                    )[0]
                )
            else:
                candidate = matrix.copy()
                candidate[indices, indices] += 1.0
                value = float(np.linalg.eigvalsh(candidate)[0])
            if value > best_value:
                best_value = value
                best_node = node
        chosen.append(best_node)
        remaining.remove(best_node)
    return np.sort(np.asarray(chosen, dtype=int))

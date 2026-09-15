"""The two and only two reconstruction algorithms allowed by D0/A-01."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


__all__ = ["lapreg_reconstruct", "bandlimited_ls"]


def lapreg_reconstruct(
    samples: ArrayLike,
    observations: ArrayLike,
    laplacian: ArrayLike,
    mu: float,
) -> NDArray[np.float64]:
    """Solve ||z_S-y||^2 + mu*z.T*L*z in closed form."""
    sample_index = np.asarray(samples, dtype=int)
    y = np.asarray(observations, dtype=float)
    L = np.asarray(laplacian, dtype=float)
    was_vector = y.ndim == 1
    if was_vector:
        y = y[:, None]
    if y.shape[0] != sample_index.size:
        raise ValueError("observations must have one row per sampled node")
    system = float(mu) * L.copy()
    system[sample_index, sample_index] += 1.0
    right_hand_side = np.zeros((L.shape[0], y.shape[1]), dtype=float)
    right_hand_side[sample_index, :] = y
    reconstruction = np.linalg.solve(system, right_hand_side)
    return reconstruction[:, 0] if was_vector else reconstruction


def bandlimited_ls(
    samples: ArrayLike,
    observations: ArrayLike,
    eigenvectors: ArrayLike,
    r: int,
) -> tuple[NDArray[np.float64], float]:
    """A-01 bandlimited minimum-norm least squares plus cond(U_S,:r)."""
    sample_index = np.asarray(samples, dtype=int)
    y = np.asarray(observations, dtype=float)
    basis = np.asarray(eigenvectors, dtype=float)[:, : int(r)]
    sampled_basis = basis[sample_index, :]
    condition = float(np.linalg.cond(sampled_basis))
    coefficients, *_ = np.linalg.lstsq(sampled_basis, y, rcond=None)
    return basis @ coefficients, condition


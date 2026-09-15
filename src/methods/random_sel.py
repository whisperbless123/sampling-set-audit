"""B1 Random sampling-set selector (zero pipeline-evaluation budget)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def select(n: int, k: int, seed: int) -> NDArray[np.int64]:
    if not 0 < k <= n:
        raise ValueError("k must satisfy 0 < k <= n")
    return np.sort(np.random.default_rng(seed).choice(n, size=k, replace=False))


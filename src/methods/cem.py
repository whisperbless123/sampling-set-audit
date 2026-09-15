"""M1 cross-entropy method with an exactly auditable evaluation budget."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def select(
    n: int,
    k: int,
    seed: int,
    objective: Callable[[np.ndarray], float],
    population: int = 50,
    elite: int = 10,
    generations: int = 40,
) -> tuple[np.ndarray, float]:
    if population != 50 or elite != 10 or population * generations not in {500, 2000, 8000}:
        raise ValueError("frozen CEM configuration requires population=50, elite=10, and E in {500, 2000, 8000}")
    rng = np.random.default_rng(seed)
    weights = np.ones(n, dtype=float)
    best_samples: np.ndarray | None = None
    best_score = np.inf
    for _ in range(generations):
        candidates = [
            np.sort(rng.choice(n, size=k, replace=False, p=weights / weights.sum()))
            for _ in range(population)
        ]
        scores = np.asarray([objective(samples) for samples in candidates], dtype=float)
        generation_order = np.argsort(scores, kind="stable")
        if scores[generation_order[0]] < best_score:
            best_score = float(scores[generation_order[0]])
            best_samples = candidates[int(generation_order[0])].copy()
        elite_masks = np.zeros((elite, n), dtype=float)
        for row, index in enumerate(generation_order[:elite]):
            elite_masks[row, candidates[int(index)]] = 1.0
        weights = np.maximum(np.mean(elite_masks, axis=0), 1e-6)
    if best_samples is None:
        raise RuntimeError("CEM produced no candidate")
    return best_samples, best_score

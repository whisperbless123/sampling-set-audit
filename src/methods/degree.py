"""B2 degree-greedy baseline."""

from __future__ import annotations

import networkx as nx
import numpy as np


def select(graph: nx.Graph, k: int) -> np.ndarray:
    ranked = sorted(graph.nodes(), key=lambda node: (-graph.degree(node), int(node)))
    return np.sort(np.asarray(ranked[:k], dtype=int))


"""Frozen Axis-S graph-signal generators."""

from __future__ import annotations

from collections.abc import Sequence

import networkx as nx
import numpy as np
from numpy.typing import NDArray


Array = NDArray[np.float64]


def laplacian_eigh(graph: nx.Graph) -> tuple[Array, Array]:
    nodes = sorted(graph.nodes())
    laplacian = nx.laplacian_matrix(graph, nodelist=nodes).toarray().astype(float)
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    return eigenvalues, eigenvectors


def _generator(seed: int | np.random.Generator) -> np.random.Generator:
    return seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)


def s1(
    graph: nx.Graph,
    n_signals: int,
    seed: int | np.random.Generator,
    r: int | None = None,
    spectral: tuple[Array, Array] | None = None,
) -> Array:
    """S1: exactly bandlimited signals x=U[:, :r]c."""
    _, eigenvectors = laplacian_eigh(graph) if spectral is None else spectral
    rank = int(np.ceil(0.1 * graph.number_of_nodes())) if r is None else int(r)
    coefficients = _generator(seed).standard_normal((rank, n_signals))
    return eigenvectors[:, :rank] @ coefficients


def s2(
    graph: nx.Graph,
    n_signals: int,
    seed: int | np.random.Generator,
    epsilon: float = 1e-2,
    spectral: tuple[Array, Array] | None = None,
) -> Array:
    """S2: samples from N(0, (L+epsilon I)^-1)."""
    eigenvalues, eigenvectors = laplacian_eigh(graph) if spectral is None else spectral
    coefficients = _generator(seed).standard_normal(
        (graph.number_of_nodes(), n_signals)
    )
    coefficients /= np.sqrt(eigenvalues[:, None] + epsilon)
    return eigenvectors @ coefficients


def _cluster_support(
    graph: nx.Graph, size: int, rng: np.random.Generator
) -> list[int]:
    if graph.graph.get("family") == "G2":
        communities: dict[int, list[int]] = {}
        for node, data in graph.nodes(data=True):
            communities.setdefault(int(data["community"]), []).append(int(node))
        eligible = [nodes for nodes in communities.values() if len(nodes) >= size]
        nodes = eligible[int(rng.integers(len(eligible)))]
        return sorted(int(v) for v in rng.choice(nodes, size=size, replace=False))

    center = int(rng.choice(list(graph.nodes())))
    distances = nx.single_source_shortest_path_length(graph, center)
    if len(distances) < size:
        raise ValueError("the selected connected component is smaller than S3 support")
    tie_breaks = {node: float(rng.random()) for node in distances}
    ordered = sorted(distances, key=lambda node: (distances[node], tie_breaks[node]))
    return sorted(int(v) for v in ordered[:size])


def s3(
    graph: nx.Graph,
    n_signals: int,
    seed: int | np.random.Generator,
    return_supports: bool = False,
    spectral: tuple[Array, Array] | None = None,
) -> Array | tuple[Array, Sequence[tuple[int, ...]]]:
    """S3: S2 background plus a 5%-node single-community/neighborhood spike."""
    rng = _generator(seed)
    background = s2(graph, n_signals, rng, spectral=spectral)
    output = background.copy()
    support_size = int(round(0.05 * graph.number_of_nodes()))
    supports: list[tuple[int, ...]] = []
    for column in range(n_signals):
        support = _cluster_support(graph, support_size, rng)
        amplitude = 5.0 * float(np.std(background[:, column]))
        signs = rng.choice(np.array([-1.0, 1.0]), size=support_size)
        output[support, column] += amplitude * signs
        supports.append(tuple(support))
    if return_supports:
        return output, supports
    return output

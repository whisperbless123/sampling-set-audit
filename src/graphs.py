"""Synthetic graph families and degree-preserving structural drift."""

from __future__ import annotations

import math

import networkx as nx


def _validate_n(n: int) -> None:
    if n < 10:
        raise ValueError("n must be at least 10")


def generate_graph(family: str, n: int, seed: int) -> nx.Graph:
    """Generate one frozen Axis-G graph instance."""
    _validate_n(n)
    family = family.upper()
    if family == "G1":
        graph = nx.gnp_random_graph(n, 8.0 / (n - 1), seed=seed)
    elif family == "G2":
        if n % 4:
            raise ValueError("G2 requires n divisible by four")
        community_size = n // 4
        p_out = 8.0 / (8 * (community_size - 1) + (n - community_size))
        p_in = 8.0 * p_out
        probabilities = [
            [p_in if i == j else p_out for j in range(4)] for i in range(4)
        ]
        graph = nx.stochastic_block_model(
            [community_size] * 4, probabilities, seed=seed
        )
        for community, nodes in enumerate(
            range(i * community_size, (i + 1) * community_size) for i in range(4)
        ):
            for node in nodes:
                graph.nodes[node]["community"] = community
        graph.graph.update(p_in=p_in, p_out=p_out, communities=4)
    elif family == "G3":
        graph = nx.watts_strogatz_graph(n, 8, 0.1, seed=seed)
    else:
        raise ValueError(f"unknown graph family: {family}")
    graph.graph.update(family=family, seed=int(seed), n=int(n))
    return graph


def rewire(graph: nx.Graph, rho: float, seed: int) -> nx.Graph:
    """Return a degree-sequence-preserving double-edge-swap perturbation.

    ``rho`` denotes the target fraction of edges participating in rewiring;
    one double-edge swap replaces two edges, so ceil(rho*|E|/2) swaps are used.
    """
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0, 1]")
    rewired = graph.copy()
    target_edges = int(round(rho * graph.number_of_edges()))
    swaps = int(math.ceil(target_edges / 2))
    if swaps:
        nx.double_edge_swap(
            rewired,
            nswap=swaps,
            max_tries=max(100, 50 * swaps),
            seed=seed,
        )
    rewired.graph.update(
        drift="degree_preserving_rewire",
        rho=float(rho),
        rewire_seed=int(seed),
        double_edge_swaps=swaps,
    )
    return rewired


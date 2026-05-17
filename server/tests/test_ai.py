import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai import rank_gateways, detect_anomalies
from mesh import Node


def make_test_nodes() -> list[Node]:
    return [
        Node(id="node-gw1", signal_strength=-62.0, latency_ms=4,
             is_gateway=True, bandwidth_available_mbps=45.0, generosity_score=0.91),
        Node(id="node-client1", signal_strength=-74.0, latency_ms=9,
             is_gateway=False, bandwidth_available_mbps=20.0, generosity_score=0.78),
        Node(id="node-gw2", signal_strength=-55.0, latency_ms=2,
             is_gateway=True, bandwidth_available_mbps=80.0, generosity_score=0.95),
    ]


def test_rank_gateways_returns_node():
    nodes = make_test_nodes()
    best = asyncio.run(rank_gateways(nodes))
    assert isinstance(best, Node)


def test_rank_gateways_prefers_gateway():
    nodes = make_test_nodes()
    best = asyncio.run(rank_gateways(nodes))
    # Should prefer a gateway node
    assert best.is_gateway is True


def test_rank_gateways_single_node():
    nodes = [Node(id="node-only", signal_strength=-50.0, latency_ms=1,
                  is_gateway=True, bandwidth_available_mbps=100.0)]
    best = asyncio.run(rank_gateways(nodes))
    assert best.id == "node-only"


def test_detect_anomalies_runs():
    nodes = make_test_nodes()
    # Should not raise
    asyncio.run(detect_anomalies(nodes))

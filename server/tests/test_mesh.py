import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mesh import Node, scan_neighbors


def test_node_creation():
    node = Node()
    assert node.id.startswith("node-")
    assert node.signal_strength == 0.0
    assert node.latency_ms == 0
    assert node.is_gateway is False
    assert node.bandwidth_available_mbps == 0.0
    assert node.generosity_score == 1.0


def test_node_custom_values():
    node = Node(
        id="node-test123",
        signal_strength=-62.0,
        latency_ms=5,
        is_gateway=True,
        bandwidth_available_mbps=45.0,
        generosity_score=0.91,
    )
    assert node.id == "node-test123"
    assert node.signal_strength == -62.0
    assert node.is_gateway is True


def test_scan_neighbors_returns_list():
    neighbors = asyncio.run(scan_neighbors())
    assert isinstance(neighbors, list)
    assert len(neighbors) > 0


def test_scan_neighbors_returns_nodes():
    neighbors = asyncio.run(scan_neighbors())
    for n in neighbors:
        assert isinstance(n, Node)
        assert n.id.startswith("node-")
        assert n.signal_strength < 0  # dBm is negative
        assert n.latency_ms > 0

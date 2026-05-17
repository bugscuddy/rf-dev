import asyncio
import subprocess
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Node:
    id: str = field(default_factory=lambda: f"node-{uuid.uuid4().hex[:6]}")
    signal_strength: float = 0.0   # dBm
    latency_ms: int = 0
    is_gateway: bool = False
    bandwidth_available_mbps: float = 0.0
    generosity_score: float = 1.0
    lat: float = 0.0  # latitude
    lng: float = 0.0  # longitude

async def scan_neighbors() -> List[Node]:
    """Parse batctl neighbors output into Node list."""
    try:
        result = subprocess.run(
            ["batctl", "n", "-w", "1"],
            capture_output=True, text=True, timeout=5
        )
        return _parse_batctl_output(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # batctl not available — return mock data for dev
        return _mock_neighbors()

def _parse_batctl_output(output: str) -> List[Node]:
    nodes = []
    for line in output.strip().splitlines()[2:]:  # skip header lines
        parts = line.split()
        if len(parts) >= 3:
            nodes.append(Node(
                id=parts[0],
                latency_ms=int(float(parts[2].replace("ms", "")) if "ms" in parts[2] else 0),
                signal_strength=-70.0,  # batctl doesn't expose RSSI directly
                is_gateway=False,
                bandwidth_available_mbps=0.0,
                generosity_score=1.0,
            ))
    return nodes

def _mock_neighbors() -> List[Node]:
    return [
        Node(id="node-a3f1", signal_strength=-62.0, latency_ms=4,
             is_gateway=True, bandwidth_available_mbps=45.0, generosity_score=0.91,
             lat=40.1525, lng=-74.8432),  # Levittown, PA (gateway)
        Node(id="node-b7c2", signal_strength=-74.0, latency_ms=9,
             is_gateway=False, bandwidth_available_mbps=0.0, generosity_score=0.78,
             lat=40.1527, lng=-74.8430),  # Very close
        Node(id="node-c9d3", signal_strength=-81.0, latency_ms=14,
             is_gateway=False, bandwidth_available_mbps=0.0, generosity_score=0.65,
             lat=40.1523, lng=-74.8434),  # Very close
    ]

async def advertise_as_gateway(node: Node):
    print(f"Advertising as gateway — score: {node.generosity_score:.2f}")

async def route_traffic(gateway: Node):
    # In production: subprocess.run(["ip", "route", "replace", "default", "via", gateway_ip])
    print(f"Routing via gateway: {gateway.id}")

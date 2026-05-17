import asyncio
import math
from typing import List
from mesh import Node

async def rank_gateways(neighbors: List[Node]) -> Node:
    """Score each gateway node and return the best one."""
    gateways = [n for n in neighbors if n.is_gateway]
    if not gateways:
        return Node()  # return empty node if no gateways found

    return max(gateways, key=calculate_gateway_score)

def calculate_gateway_score(node: Node) -> float:
    """
    Weighted scoring model:
    - Latency:           40% weight (lower is better)
    - Bandwidth:         35% weight (higher is better)
    - Generosity score:  15% weight (community trust)
    - Signal strength:   10% weight (higher is better)
    """
    latency_score = 1.0 / (node.latency_ms + 1)
    bandwidth_score = node.bandwidth_available_mbps / 100.0
    signal_score = (node.signal_strength + 100.0) / 100.0  # normalize dBm

    return (
        latency_score     * 0.40 +
        bandwidth_score   * 0.35 +
        node.generosity_score * 0.15 +
        signal_score      * 0.10
    )

async def detect_anomalies(neighbors: List[Node]):
    for node in neighbors:
        if node.bandwidth_available_mbps < 0:
            print(f"ANOMALY: Node {node.id} reporting negative bandwidth")
        if node.generosity_score < 0.1:
            print(f"WARNING: Node {node.id} has very low generosity score")

def predict_congestion(hour: int) -> float:
    """Sine-curve congestion model — peaks at 8pm, lowest at 4am."""
    peak_hour = 20
    normalized = abs(hour - peak_hour) / 12.0
    return 1.0 - min(normalized, 1.0)

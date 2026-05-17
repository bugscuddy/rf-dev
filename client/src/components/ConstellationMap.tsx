import { useEffect, useRef } from "react";
import type { Neighbor, NodeStatus } from "../types";

interface Props {
  neighbors: Neighbor[];
  status: NodeStatus | null;
}

export default function ConstellationMap({ neighbors, status }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = canvas.width = canvas.offsetWidth;
    const H = canvas.height = 180;
    ctx.clearRect(0, 0, W, H);

    const center = { x: W / 2, y: H / 2 };
    const angleStep = (2 * Math.PI) / Math.max(neighbors.length, 1);
    const radius = Math.min(W, H) * 0.32;

    const positions = neighbors.map((node, i) => ({
      node,
      x: center.x + radius * Math.cos(i * angleStep - Math.PI / 2),
      y: center.y + radius * Math.sin(i * angleStep - Math.PI / 2),
    }));

    // Draw edges
    positions.forEach(({ node, x, y }) => {
      const alpha = Math.min((node.signal_strength + 100) / 40, 0.8);
      ctx.beginPath();
      ctx.moveTo(center.x, center.y);
      ctx.lineTo(x, y);
      ctx.strokeStyle = node.is_gateway
        ? `rgba(0,255,136,${alpha})`
        : `rgba(100,116,139,${Math.min(alpha, 0.5)})`;
      ctx.lineWidth = node.is_gateway ? 1.5 : 1;
      ctx.setLineDash(node.is_gateway ? [] : [4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
    });

    // Draw neighbor nodes
    positions.forEach(({ node, x, y }) => {
      const color = node.is_gateway ? "#00ff88" : "#3b82f6";
      const r = node.is_gateway ? 8 : 6;
      ctx.shadowColor = color;
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = "#e2e8f0";
      ctx.font = "10px JetBrains Mono, monospace";
      ctx.textAlign = "center";
      ctx.fillText(node.id.slice(-4), x, y + r + 14);
    });

    // Draw this node (center)
    ctx.shadowColor = "#ffffff";
    ctx.shadowBlur = 20;
    ctx.beginPath();
    ctx.arc(center.x, center.y, 10, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#0a0e1a";
    ctx.font = "bold 10px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("YOU", center.x, center.y + 3);
    ctx.fillStyle = "#64748b";
    ctx.font = "9px JetBrains Mono, monospace";
    ctx.fillText(status?.node_id.slice(0, 10) ?? "this node", center.x, center.y + 26);

  }, [neighbors, status]);

  return (
    <div className="card">
      <div className="card-header">
        <h2>Mesh Constellation</h2>
        <span className="badge">{neighbors.length} visible</span>
      </div>
      <canvas ref={canvasRef} style={{ width: "100%", height: "180px", display: "block" }} />
      <div className="legend">
        <span><span className="dot green" /> Gateway</span>
        <span><span className="dot blue" /> Client Node</span>
        <span><span className="dot white" /> This Node</span>
      </div>
    </div>
  );
}

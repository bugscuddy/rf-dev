import { useEffect, useRef } from "react";
import type { Neighbor, NodeStatus } from "../types";

interface Props {
  neighbors: Neighbor[];
  status: NodeStatus | null;
}

export default function ConstellationMap({ neighbors, status }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = canvas.width = canvas.offsetWidth * 2;
    const H = canvas.height = 180 * 2;
    canvas.style.width = "100%";
    canvas.style.height = "180px";
    ctx.scale(2, 2);

    const center = { x: W / 4, y: H / 4 };
    const angleStep = (2 * Math.PI) / Math.max(neighbors.length, 1);
    const radius = Math.min(W / 2, H / 2) * 0.32;

    const positions = neighbors.map((node, i) => ({
      node,
      x: center.x + radius * Math.cos(i * angleStep - Math.PI / 2),
      y: center.y + radius * Math.sin(i * angleStep - Math.PI / 2),
    }));

    let frame = 0;

    const draw = () => {
      ctx.clearRect(0, 0, W / 2, H / 2);
      frame++;
      const t = frame / 60; // time in seconds

      // Draw signal rings from center node
      const ringCount = 3;
      for (let r = 0; r < ringCount; r++) {
        const progress = ((t * 0.5 + r / ringCount) % 1);
        const ringRadius = progress * radius * 0.4;
        const alpha = (1 - progress) * 0.15;
        ctx.beginPath();
        ctx.arc(center.x, center.y, ringRadius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Draw edges with data packet animation
      positions.forEach(({ node, x, y }, i) => {
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

        // Animated data packet traveling along the edge
        const packetProgress = ((t * 0.8 + i * 0.3) % 2) / 2;
        if (packetProgress < 1) {
          const px = center.x + (x - center.x) * packetProgress;
          const py = center.y + (y - center.y) * packetProgress;
          const packetColor = node.is_gateway ? "#00ff88" : "#60a5fa";
          ctx.beginPath();
          ctx.arc(px, py, 2, 0, Math.PI * 2);
          ctx.fillStyle = packetColor;
          ctx.shadowColor = packetColor;
          ctx.shadowBlur = 6;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Draw neighbor nodes with signal rings
      positions.forEach(({ node, x, y }) => {
        const color = node.is_gateway ? "#00ff88" : "#3b82f6";
        const r = node.is_gateway ? 7 : 5;

        // Signal ring per node
        const signalStrength = Math.abs(node.signal_strength);
        const ringProgress = (t * 0.3) % 1;
        const nodeRingR = r + ringProgress * (40 - signalStrength * 0.3);
        const ringAlpha = (1 - ringProgress) * 0.25;
        ctx.beginPath();
        ctx.arc(x, y, nodeRingR, 0, Math.PI * 2);
        ctx.strokeStyle = `${color}${Math.round(ringAlpha * 255).toString(16).padStart(2, '0')}`;
        ctx.lineWidth = 0.5;
        ctx.stroke();

        // Node dot
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Label
        ctx.fillStyle = "#e2e8f0";
        ctx.font = "9px JetBrains Mono, monospace";
        ctx.textAlign = "center";
        ctx.fillText(node.id.slice(-4), x, y + r + 13);
      });

      // Draw this node (center) with glow
      const centerGlow = 0.5 + Math.sin(t * 2) * 0.2;
      ctx.shadowColor = "#ffffff";
      ctx.shadowBlur = 15 * centerGlow;
      ctx.beginPath();
      ctx.arc(center.x, center.y, 9, 0, Math.PI * 2);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = "#0a0e1a";
      ctx.font = "bold 9px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("YOU", center.x, center.y + 3);
      ctx.fillStyle = "#64748b";
      ctx.font = "8px JetBrains Mono, monospace";
      ctx.fillText(status?.node_id.slice(0, 10) ?? "this node", center.x, center.y + 24);

      animRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => cancelAnimationFrame(animRef.current);
  }, [neighbors, status]);

  return (
    <div className="card">
      <div className="card-header">
        <h2>Mesh Constellation</h2>
        <span className="badge">{neighbors.length} visible</span>
      </div>
      <canvas ref={canvasRef} style={{ display: "block" }} />
      <div className="legend">
        <span><span className="dot green" /> Gateway</span>
        <span><span className="dot blue" /> Client Node</span>
        <span><span className="dot white" /> This Node</span>
      </div>
    </div>
  );
}

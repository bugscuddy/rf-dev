import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend
} from "recharts";
import type { MetricPoint } from "../types";

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip">
      <p className="tooltip-label">{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {p.value}{p.name === "gb_shared" ? " GB" : "%"}
        </p>
      ))}
    </div>
  );
}

interface Props { metrics: MetricPoint[]; }

export default function MetricsChart({ metrics }: Props) {
  return (
    <div className="card">
      <div className="card-header"><h2>30-Day Contribution</h2></div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={metrics} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fontSize: 9, fill: "#64748b" }}
                 tickFormatter={(d: string) => d.slice(5)} />
          <YAxis tick={{ fontSize: 9, fill: "#64748b" }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: "11px" }} />
          <Line type="monotone" dataKey="gb_shared" name="gb_shared"
                stroke="#00ff88" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="uptime_pct" name="uptime_pct"
                stroke="#3b82f6" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

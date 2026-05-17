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
          {p.name}: {p.value}{p.name === "Data Shared (GB)" ? " GB" : "%"}
        </p>
      ))}
    </div>
  );
}

interface Props { metrics: MetricPoint[]; isGatewayActive: boolean; }

export default function MetricsChart({ metrics, isGatewayActive }: Props) {

  return (
    <div className="card">
      <div className="card-header"><h2>30-Day Contribution</h2></div>

      {/* Gateway activity strip */}
      <div className="gateway-strip">
        {metrics.map((m, i) => {
          // Last cell reflects current real-time gateway state
          const isActive = i === metrics.length - 1 ? isGatewayActive : m.is_gateway;
          return (
            <div
              key={i}
              className={`gateway-cell ${isActive ? "active" : "inactive"}`}
              title={`${m.date}: ${isActive ? "Gateway Active" : "Inactive"}`}
            />
          );
        })}
      </div>
      <div className="gateway-strip-legend">
        <span className={isGatewayActive ? "current-status" : ""}>
          <span className={`strip-dot active ${isGatewayActive ? "highlighted" : ""}`} /> Gateway Active
        </span>
        <span className={!isGatewayActive ? "current-status" : ""}>
          <span className={`strip-dot inactive ${!isGatewayActive ? "highlighted" : ""}`} /> Inactive
        </span>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={metrics} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fontSize: 9, fill: "#64748b" }}
                 tickFormatter={(d: string) => d.slice(5)} />
          <YAxis tick={{ fontSize: 9, fill: "#64748b" }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: "11px" }} />
          <Line type="monotone" dataKey="gb_shared" name="Data Shared (GB)"
                stroke="#00ff88" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="uptime_pct" name="Uptime (%)"
                stroke="#3b82f6" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

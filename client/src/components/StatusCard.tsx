import type { NodeStatus } from "../types";

const POWER_COLORS: Record<NodeStatus["power_mode"], string> = {
  FullOperation: "#00ff88",
  Reduced: "#ffcc00",
  LowPower: "#ff8800",
  Sleep: "#ff4444",
};

interface Props { status: NodeStatus | null; }

export default function StatusCard({ status }: Props) {
  if (!status) return (
    <div className="card">
      <div className="skeleton-grid">
        {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton" />)}
      </div>
    </div>
  );

  return (
    <div className="card">
      <div className="card-header">
        <h2>Node Status</h2>
        <span className="version">v{status.version}</span>
      </div>
      <div className="stat-grid">
        <Stat label="Neighbors"   value={String(status.neighbors)}                          icon="⬡" />
        <Stat label="Data Shared" value={`${status.bandwidth_shared_gb} GB`}                icon="↑" />
        <Stat label="Uptime"      value={`${status.uptime_hours}h`}                         icon="⏱" />
        <Stat label="Generosity"  value={`${(status.generosity_score * 100).toFixed(0)}%`}  icon="♥" />
        <Stat label="Gateway"     value={status.is_gateway ? "Active ✓" : "Inactive"}       icon="⊙" />
        <Stat label="Power Mode"  value={status.power_mode} icon="⚡"
              color={POWER_COLORS[status.power_mode]} />
      </div>
    </div>
  );
}

interface StatProps { label: string; value: string; icon: string; color?: string; }
function Stat({ label, value, icon, color }: StatProps) {
  return (
    <div className="stat">
      <span className="stat-icon">{icon}</span>
      <span className="stat-label">{label}</span>
      <span className="stat-value" style={{ color: color ?? "var(--text-h)" }}>{value}</span>
    </div>
  );
}

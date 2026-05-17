import type { Neighbor } from "../types";

interface Props { neighbors: Neighbor[]; }

export default function NeighborMap({ neighbors }: Props) {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Mesh Neighbors</h2>
        <span className="badge">{neighbors.length} nodes</span>
      </div>
      {neighbors.length === 0 ? (
        <p className="empty">Scanning for neighbors...</p>
      ) : (
        <ul className="neighbor-list">
          {neighbors.map(n => (
            <li key={n.id} className={`neighbor ${n.is_gateway ? "gateway" : ""}`}>
              <div className="neighbor-top">
                <span className="neighbor-id">{n.id}</span>
                {n.is_gateway && <span className="gateway-badge">GATEWAY</span>}
              </div>
              <div className="neighbor-stats">
                <span>{n.signal_strength} dBm</span>
                <span>{n.latency_ms}ms</span>
                {n.is_gateway && <span>{n.bandwidth_available_mbps} Mbps</span>}
              </div>
              <div className="bar-row">
                <span className="bar-label">Generosity</span>
                <div className="generosity-bar">
                  <div style={{ width: `${n.generosity_score * 100}%` }} />
                </div>
                <span className="bar-pct">{(n.generosity_score * 100).toFixed(0)}%</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

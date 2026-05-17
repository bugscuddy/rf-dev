import { useState, useEffect } from "react";
import "./App.css";
import "./index.css";
import StatusCard from "./components/StatusCard";
import Controls from "./components/Controls";
import MetricsChart from "./components/MetricsChart";
import ConstellationMap from "./components/ConstellationMap";
import NeighborMap from "./components/NeighborMap";
import type { NodeStatus, Neighbor, MetricPoint } from "./types";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
type Tab = "dashboard" | "network" | "controls";

export default function App() {
  const [status, setStatus] = useState<NodeStatus | null>(null);
  const [neighbors, setNeighbors] = useState<Neighbor[]>([]);
  const [metrics, setMetrics] = useState<MetricPoint[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("dashboard");

  const fetchAll = async () => {
    try {
      const [s, n, m] = await Promise.all([
        fetch(`${API}/api/status`).then(r => r.json() as Promise<NodeStatus>),
        fetch(`${API}/api/neighbors`).then(r => r.json() as Promise<Neighbor[]>),
        fetch(`${API}/api/metrics/history`).then(r => r.json() as Promise<MetricPoint[]>),
      ]);
      setStatus(s);
      setNeighbors(n);
      setMetrics(m);
    } catch {
      console.warn("API unreachable — running in demo mode");
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 10_000);
    return () => clearInterval(interval);
  }, []);

  // Refetch data when tab changes to ensure fresh data
  useEffect(() => {
    fetchAll();
  }, [activeTab]);

  const tabs: Tab[] = ["dashboard", "network", "controls"];

  return (
    <div className="app">
      <header>
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">NodeFree</span>
        </div>
        <div className="header-right">
          <span className={`status-dot ${status ? "online" : "offline"}`} />
          <span className="node-id">{status?.node_id.slice(0, 12) ?? "connecting..."}</span>
        </div>
      </header>

      <nav className="tabs">
        {tabs.map(tab => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      <main>
        {activeTab === "dashboard" && (
          <>
            <StatusCard status={status} />
            <MetricsChart metrics={metrics} isGatewayActive={status?.is_gateway ?? false} />
          </>
        )}
        {activeTab === "network" && (
          <>
            <ConstellationMap neighbors={neighbors} status={status} />
            <NeighborMap neighbors={neighbors} />
          </>
        )}
        {activeTab === "controls" && (
          <Controls api={API} status={status} onRefresh={fetchAll} />
        )}
      </main>
    </div>
  );
}

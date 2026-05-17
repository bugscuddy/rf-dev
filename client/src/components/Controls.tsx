import { useState } from "react";
import type { NodeStatus, SuccessResponse } from "../types";

interface Props { api: string; status: NodeStatus | null; }

export default function Controls({ api, status }: Props) {
  const [cap, setCap] = useState<number>(50);
  const [msg, setMsg] = useState<string | null>(null);
  const [msgType, setMsgType] = useState<"success" | "error">("success");

  const post = async (endpoint: string, body: Record<string, unknown>) => {
    try {
      const res = await fetch(`${api}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json() as SuccessResponse;
      setMsg(data.message);
      setMsgType("success");
    } catch {
      setMsg("Could not reach node API");
      setMsgType("error");
    }
    setTimeout(() => setMsg(null), 4000);
  };

  return (
    <div className="controls-page">
      <div className="card">
        <div className="card-header"><h2>Gateway Mode</h2></div>
        <p className="control-desc">
          Enable to share your internet connection with the mesh network.
        </p>
        <div className="control-row">
          <button className="btn-green" onClick={() => post("/api/set-gateway", { enabled: true })}>
            Enable Gateway
          </button>
          <button className="btn-red" onClick={() => post("/api/set-gateway", { enabled: false })}>
            Disable Gateway
          </button>
        </div>
        <div className="current-state">
          Current: <strong>{status?.is_gateway ? "Active ✓" : "Inactive"}</strong>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h2>Bandwidth Cap</h2></div>
        <p className="control-desc">
          Limit how much of your connection is shared with neighbors.
        </p>
        <div className="control-row">
          <input type="range" min={1} max={500} value={cap}
                 onChange={e => setCap(Number(e.target.value))} />
          <span className="cap-value">{cap} Mbps</span>
        </div>
        <button className="btn-green"
                onClick={() => post("/api/set-bandwidth-cap", { cap_mbps: cap })}>
          Apply Cap
        </button>
      </div>

      {msg && <div className={`toast ${msgType}`}>{msg}</div>}
    </div>
  );
}

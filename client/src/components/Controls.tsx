import { useState, useEffect } from "react";
import type { NodeStatus, SuccessResponse } from "../types";

interface Props { api: string; status: NodeStatus | null; onRefresh: () => void; }

export default function Controls({ api, status, onRefresh }: Props) {
  const [cap, setCap] = useState<number>(50);
  const [msg, setMsg] = useState<string | null>(null);
  const [msgType, setMsgType] = useState<"success" | "error">("success");
  const [token, setToken] = useState<string>("");
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [tokenInput, setTokenInput] = useState<string>("");

  useEffect(() => {
    const saved = localStorage.getItem("meshwork_token");
    if (saved) {
      setToken(saved);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = async () => {
    try {
      const res = await fetch(`${api}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: tokenInput }),
      });
      const data = await res.json();
      if (data.success) {
        setToken(tokenInput);
        setIsAuthenticated(true);
        localStorage.setItem("meshwork_token", tokenInput);
        setMsg("Authenticated successfully");
        setMsgType("success");
      } else {
        setMsg("Invalid token");
        setMsgType("error");
      }
    } catch {
      setMsg("Could not reach node API");
      setMsgType("error");
    }
    setTimeout(() => setMsg(null), 4000);
  };

  const handleLogout = () => {
    setToken("");
    setIsAuthenticated(false);
    localStorage.removeItem("meshwork_token");
    setMsg("Logged out");
    setMsgType("success");
    setTimeout(() => setMsg(null), 4000);
  };

  const post = async (endpoint: string, body: Record<string, unknown>) => {
    if (!isAuthenticated) {
      setMsg("Authentication required");
      setMsgType("error");
      setTimeout(() => setMsg(null), 4000);
      return;
    }
    try {
      const res = await fetch(`${api}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      if (res.status === 401 || res.status === 403) {
        setIsAuthenticated(false);
        localStorage.removeItem("meshwork_token");
        setMsg("Session expired — please re-authenticate");
        setMsgType("error");
        setTimeout(() => setMsg(null), 4000);
        return;
      }
      const data = await res.json() as SuccessResponse;
      setMsg(data.message);
      setMsgType("success");
      onRefresh();
    } catch {
      setMsg("Could not reach node API");
      setMsgType("error");
    }
    setTimeout(() => setMsg(null), 4000);
  };

  if (!isAuthenticated) {
    return (
      <div className="controls-page">
        <div className="card">
          <div className="card-header"><h2>Authentication Required</h2></div>
          <p className="control-desc">
            Enter your access token to manage this node. The token was displayed on first server boot.
          </p>
          <div className="control-row">
            <input
              type="password"
              className="token-input"
              placeholder="Paste access token..."
              value={tokenInput}
              onChange={e => setTokenInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
            />
          </div>
          <button className="btn-green" onClick={handleLogin}>
            Authenticate
          </button>
        </div>
        {msg && <div className={`toast ${msgType}`}>{msg}</div>}
      </div>
    );
  }

  return (
    <div className="controls-page">
      <div className="card">
        <div className="card-header">
          <h2>Gateway Mode</h2>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
        <p className="control-desc">
          Enable to share your internet connection with the mesh network.
        </p>
        <div className="control-row">
          <button className={`btn-green ${status?.is_gateway ? "btn-active" : ""}`} onClick={() => post("/api/set-gateway", { enabled: true })}>
            Enable Gateway
          </button>
          <button className={`btn-red ${!status?.is_gateway ? "btn-active" : ""}`} onClick={() => post("/api/set-gateway", { enabled: false })}>
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

export interface NodeStatus {
  node_id: string;
  neighbors: number;
  is_gateway: boolean;
  bandwidth_shared_gb: number;
  uptime_hours: number;
  generosity_score: number;
  power_mode: "FullOperation" | "Reduced" | "LowPower" | "Sleep";
  version: string;
}

export interface Neighbor {
  id: string;
  signal_strength: number;
  latency_ms: number;
  is_gateway: boolean;
  generosity_score: number;
  bandwidth_available_mbps: number;
}

export interface MetricPoint {
  date: string;
  gb_shared: number;
  uptime_pct: number;
}

export interface SuccessResponse {
  success: boolean;
  message: string;
}

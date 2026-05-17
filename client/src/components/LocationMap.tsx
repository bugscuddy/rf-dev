import { useEffect, useRef } from "react";
import type { Neighbor, NodeStatus } from "../types";

declare global {
  interface Window {
    L: any;
  }
}

interface Props {
  neighbors: Neighbor[];
  status: NodeStatus | null;
}

export default function LocationMap({ neighbors, status }: Props) {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapContainerRef.current || !window.L) return;

    // Initialize map centered on Levittown, PA
    const map = window.L.map(mapContainerRef.current).setView([40.1525, -74.8432], 13);
    
    // Add satellite imagery tiles (Esri World Imagery)
    window.L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      attribution: 'Tiles &copy; Esri'
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !window.L) return;

    const map = mapRef.current;

    // Clear existing markers
    map.eachLayer((layer: any) => {
      if (layer instanceof window.L.Marker) {
        map.removeLayer(layer);
      }
    });

    // Add center node (this node)
    const centerLat = 40.1525;
    const centerLng = -74.8432;
    const isGateway = status?.is_gateway ?? false;
    
    const centerColor = isGateway ? "#4ade80" : "#f87171";
    const centerIcon = window.L.divIcon({
      className: "custom-marker",
      html: `<div style="
        background: ${centerColor};
        border: 2px solid #0a0e1a;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        box-shadow: 0 0 10px ${centerColor};
      "></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });

    window.L.marker([centerLat, centerLng], { icon: centerIcon })
      .addTo(map)
      .bindPopup(`<b>YOU</b><br>${status?.node_id ?? "this node"}`);

    // Add connection lines from center to neighbors first
    neighbors.forEach((neighbor) => {
      window.L.polyline(
        [[centerLat, centerLng], [neighbor.lat, neighbor.lng]],
        {
          color: neighbor.is_gateway ? (isGateway ? "#4ade80" : "#f87171") : "#60a5fa",
          weight: neighbor.is_gateway ? 4 : 3,
          opacity: 1.0,
          dashArray: neighbor.is_gateway ? undefined : "5, 5"
        }
      ).addTo(map);
    });

    // Add neighbor markers
    neighbors.forEach((neighbor) => {
      const color = neighbor.is_gateway ? (isGateway ? "#4ade80" : "#f87171") : "#3b82f6";
      const icon = window.L.divIcon({
        className: "custom-marker",
        html: `<div style="
          background: ${color};
          border: 2px solid #0a0e1a;
          border-radius: 50%;
          width: ${neighbor.is_gateway ? 14 : 10}px;
          height: ${neighbor.is_gateway ? 14 : 10}px;
          box-shadow: 0 0 8px ${color};
        "></div>`,
        iconSize: [neighbor.is_gateway ? 14 : 10, neighbor.is_gateway ? 14 : 10],
        iconAnchor: [neighbor.is_gateway ? 7 : 5, neighbor.is_gateway ? 7 : 5]
      });

      window.L.marker([neighbor.lat, neighbor.lng], { icon: icon })
        .addTo(map)
        .bindPopup(`
          <b>${neighbor.id}</b><br>
          Signal: ${neighbor.signal_strength} dBm<br>
          Latency: ${neighbor.latency_ms}ms<br>
          Gateway: ${neighbor.is_gateway ? "Yes" : "No"}
        `);
    });

    // Fit bounds to show all markers
    if (neighbors.length > 0) {
      const bounds = window.L.latLngBounds([
        [centerLat, centerLng],
        ...neighbors.map(n => [n.lat, n.lng] as [number, number])
      ]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [neighbors, status]);

  return (
    <div className="card">
      <div className="card-header">
        <h2>Mesh Map</h2>
        <span className={`badge ${status?.is_gateway ? "badge-green" : "badge-red"}`}>
          {status?.is_gateway ? "Gateway Active" : "Gateway Inactive"}
        </span>
      </div>
      <div 
        ref={mapContainerRef} 
        style={{ 
          height: "300px", 
          width: "100%", 
          borderRadius: "10px",
          overflow: "hidden"
        }} 
      />
      <div className="legend">
        <span><span className="dot green" /> Gateway</span>
        <span><span className="dot blue" /> Client Node</span>
        <span><span className="dot white" /> This Node</span>
      </div>
    </div>
  );
}

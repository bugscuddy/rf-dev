from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import asyncio
import logging
import os
import uuid

from mesh import Node, scan_neighbors as _scan_neighbors
from energy import get_power_mode, read_harvested_power_mw, PowerMode
from db import init_db, get_metrics_history, log_metric
from tvws import get_backhaul_status
from auth import init_auth, require_auth, verify_token
from serial_link import get_link as _get_serial_link

init_db()
logger = logging.getLogger(__name__)

# Generate auth token on first boot
_boot_token = init_auth()
if _boot_token:
    print(f"\n{'='*60}")
    print(f"  FIRST BOOT - Save this access token (shown only once):")
    print(f"  {_boot_token}")
    print(f"{'='*60}\n")

app = FastAPI(title="Meshwork API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

NODE_ID = f"node-{uuid.uuid4().hex[:8]}"
_state_lock = asyncio.Lock()
_is_gateway = False
_bandwidth_cap = 50.0

def get_gateway_state() -> bool:
    return _is_gateway

def get_bandwidth_cap() -> float:
    return _bandwidth_cap

# ---- Request/Response Models ----

class StatusResponse(BaseModel):
    node_id: str
    neighbors: int
    is_gateway: bool
    bandwidth_shared_gb: float
    uptime_hours: int
    generosity_score: float
    power_mode: str
    version: str

class NeighborResponse(BaseModel):
    id: str
    signal_strength: float
    latency_ms: int
    is_gateway: bool
    generosity_score: float
    bandwidth_available_mbps: float

class MetricPoint(BaseModel):
    date: str
    gb_shared: float
    uptime_pct: float
    is_gateway: bool = False

class GatewayToggle(BaseModel):
    enabled: bool

class BandwidthCap(BaseModel):
    cap_mbps: float

class SuccessResponse(BaseModel):
    success: bool
    message: str

# ---- Routes ----

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    try:
        power_mw = read_harvested_power_mw()
        mode = get_power_mode(power_mw)
        response = StatusResponse(
            node_id=NODE_ID,
            neighbors=len(await _scan_neighbors()),
            is_gateway=_is_gateway,
            bandwidth_shared_gb=12.4,
            uptime_hours=168,
            generosity_score=0.87,
            power_mode=mode.value,
            version="0.1.0",
        )
        logger.debug(f"Status request: neighbors={response.neighbors}, mode={response.power_mode}")
        return response
    except Exception as e:
        logger.error(f"Error in /api/status: {e}", exc_info=True)
        raise

@app.get("/api/neighbors", response_model=List[NeighborResponse])
async def get_neighbors():
    try:
        neighbors = await _scan_neighbors()
        response = [NeighborResponse(
            id=n.id,
            signal_strength=n.signal_strength,
            latency_ms=n.latency_ms,
            is_gateway=n.is_gateway,
            generosity_score=n.generosity_score,
            bandwidth_available_mbps=n.bandwidth_available_mbps,
        ) for n in neighbors]
        logger.debug(f"Neighbors request: {len(response)} neighbors")
        return response
    except Exception as e:
        logger.error(f"Error in /api/neighbors: {e}", exc_info=True)
        raise

@app.get("/api/metrics/history", response_model=List[MetricPoint])
async def get_metrics():
    try:
        rows = get_metrics_history(30)
        if not rows:
            # seed with mock data if DB empty
            response = [MetricPoint(date=f"2026-04-{i+1:02d}",
                                gb_shared=round(0.3 + i * 0.1, 1),
                                uptime_pct=95.0 + (i % 5),
                                is_gateway=i % 3 == 0)  # Every 3rd day as gateway
                    for i in range(30)]
            logger.debug("Metrics request: using mock data (DB empty)")
            return response
        logger.debug(f"Metrics request: {len(rows)} historical records")
        return [MetricPoint(**r) for r in rows]
    except Exception as e:
        logger.error(f"Error in /api/metrics/history: {e}", exc_info=True)
        raise

class AuthRequest(BaseModel):
    token: str

@app.post("/api/auth/login")
async def login(body: AuthRequest):
    try:
        if verify_token(body.token):
            logger.info("Authentication successful")
            return {"success": True, "message": "Authenticated"}
        logger.warning("Authentication failed: invalid token")
        return {"success": False, "message": "Invalid token"}
    except Exception as e:
        logger.error(f"Error in /api/auth/login: {e}", exc_info=True)
        raise

@app.get("/api/auth/token")
async def get_token():
    """
    Development endpoint to retrieve the current authentication token.
    This is INSECURE for production - only for local development.
    """
    try:
        # Read the stored hash
        from auth import get_stored_hash, _generate_token, _hash_token
        stored_hash = get_stored_hash()
        if not stored_hash:
            # Generate a new token if none exists
            token = _generate_token()
            hashed = _hash_token(token)
            with open(TOKEN_FILE, "w") as f:
                f.write(hashed)
            logger.warning("Generated new token via /api/auth/token endpoint")
            return {"token": token}
        
        # We can't reverse the hash, so we need to generate a new one
        logger.warning("Token reset via /api/auth/token endpoint")
        token = _generate_token()
        hashed = _hash_token(token)
        with open(TOKEN_FILE, "w") as f:
            f.write(hashed)
        return {"token": token}
    except Exception as e:
        logger.error(f"Error in /api/auth/token: {e}", exc_info=True)
        raise

@app.post("/api/set-gateway", response_model=SuccessResponse)
async def set_gateway(body: GatewayToggle, _token: str = Depends(require_auth)):
    try:
        global _is_gateway
        async with _state_lock:
            _is_gateway = body.enabled
        # Log the gateway status change to metrics
        log_metric(12.4, 95.0, _is_gateway)
        logger.info(f"Gateway mode set to {body.enabled}")
        return SuccessResponse(success=True, message=f"Gateway mode set to {body.enabled}")
    except Exception as e:
        logger.error(f"Error in /api/set-gateway: {e}", exc_info=True)
        raise

@app.post("/api/set-bandwidth-cap", response_model=SuccessResponse)
async def set_bandwidth_cap(body: BandwidthCap, _token: str = Depends(require_auth)):
    try:
        global _bandwidth_cap
        async with _state_lock:
            _bandwidth_cap = body.cap_mbps
        logger.info(f"Bandwidth cap set to {body.cap_mbps} Mbps")
        return SuccessResponse(success=True, message=f"Bandwidth cap set to {body.cap_mbps} Mbps")
    except Exception as e:
        logger.error(f"Error in /api/set-bandwidth-cap: {e}", exc_info=True)
        raise

@app.get("/api/tvws/status")
async def tvws_status():
    try:
        status = await get_backhaul_status()
        logger.debug(f"TVWS status request: connected={status.get('connected', False)}")
        return status
    except Exception as e:
        logger.error(f"Error in /api/tvws/status: {e}", exc_info=True)
        raise

@app.get("/api/firmware/status")
async def firmware_status():
    try:
        link = _get_serial_link()
        if link is None:
            logger.warning("Firmware status requested but serial link not initialized")
            return {"connected": False, "message": "Serial link not initialized"}
        power = link.get_power()
        radio = link.get_radio()
        response = {
            "connected": True,
            "firmware_ready": link.firmware_ready,
            "power": {
                "harvested_mw": power.harvested_mw,
                "battery_v": power.battery_v,
                "mode": power.mode,
            },
            "radio": {
                "tvws_connected": radio.connected,
                "frequency_mhz": radio.frequency_mhz,
                "rssi_dbm": radio.rssi_dbm,
            },
            "alerts": link.get_alerts(),
        }
        logger.debug(f"Firmware status request: ready={link.firmware_ready}")
        return response
    except Exception as e:
        logger.error(f"Error in /api/firmware/status: {e}", exc_info=True)
        raise

@app.get("/")
async def root():
    return {"status": "active", "service": "Meshwork API", "version": "0.1"}

# Serve React build at root (must be last)
static_dir = os.path.join(os.path.dirname(__file__), "../Meshwork-ui/dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

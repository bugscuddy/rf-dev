# NodeFree — Project Instructions for Windsurf

## Mission
Make internet access as free and universally available as air — owned by no one,
controlled by no one, and available to everyone.

NodeFree is an open-source, self-powered mesh networking device and software platform
that gives every person within 300 feet free community internet with zero monthly fee,
zero carrier, zero technical knowledge, and zero setup required.

---

## What We Are Building

A small physical device (target cost: ~$40) combined with an AI-powered software stack that:

1. Harvests ambient energy (RF, solar, thermal) to power itself — no outlet, no battery
2. Uses free, unlicensed TV White Space (TVWS) spectrum for legal broadband backhaul
3. Self-organizes into a neighborhood mesh network with neighboring NodeFree devices
4. Distributes free internet to all users in range automatically using AI-optimized routing
5. Requires zero configuration, zero accounts, and zero ongoing cost for end users

---

## Tech Stack

### Backend (nodefree-py/)
- Language: Python 3.12+
- Framework: FastAPI with Uvicorn (async)
- Database: SQLite via Python stdlib sqlite3
- AI Mesh Agent: asyncio loop running every 30s
- Key modules:
  - main.py       — boot, runs API server + mesh loop concurrently
  - api.py        — FastAPI routes, Pydantic models
  - mesh.py       — batctl neighbor scanning, Node dataclass
  - ai.py         — gateway scoring, anomaly detection, congestion prediction
  - energy.py     — power mode management, harvesting IC interface
  - db.py         — SQLite metrics logging

### Frontend (nodefree-ui/)
- Language: TypeScript (strict mode)
- Framework: React 18 + Vite
- Charts: Recharts
- Key files:
  - src/types.ts                          — all shared TypeScript interfaces
  - src/App.tsx                           — tabbed layout, API polling every 10s
  - src/components/StatusCard.tsx         — node health display
  - src/components/ConstellationMap.tsx   — live HTML5 canvas mesh visualization
  - src/components/NeighborMap.tsx        — neighbor list with generosity scores
  - src/components/MetricsChart.tsx       — 30-day contribution line chart
  - src/components/Controls.tsx           — gateway toggle, bandwidth cap

---

## Architecture Principles

- **Fully decentralized** — no cloud server, no central authority, no single point of failure
- **Zero config** — every device must work out of the box with no user setup
- **AI-first routing** — the mesh brain scores gateways by latency (40%), bandwidth (35%),
  generosity score (15%), and signal strength (10%)
- **Graceful power degradation** — four power modes (FullOperation → Reduced → LowPower → Sleep)
  based on harvested milliwatts
- **Open source** — every line of code is public, auditable, and forkable

---

## API Endpoints (FastAPI — port 8080)

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | /api/status               | Node health, power mode, uptime    |
| GET    | /api/neighbors            | Live mesh neighbor list            |
| GET    | /api/metrics/history      | 30-day contribution data           |
| POST   | /api/set-gateway          | Toggle gateway mode on/off         |
| POST   | /api/set-bandwidth-cap    | Set max bandwidth share (Mbps)     |

The React frontend is served from /api/static after running: npm run build

---

## What Still Needs to Be Built

- [ ] TVWS radio driver (tvws.py) — interface with TVWS hardware for free spectrum backhaul
- [ ] Real batctl neighbor parsing — connect mesh.py scan_neighbors() to live hardware
- [ ] Energy harvesting IC reader — connect energy.py to AEM10941 or BQ25570 via I2C (smbus2)
- [ ] SQLite metrics logging — wire db.py log_metric() into the main heartbeat loop
- [ ] Dashboard authentication — protect the control panel from unauthorized access
- [ ] Visual node constellation — animate the ConstellationMap with live signal pulsing
- [ ] Hardware prototype — GL.iNet GL-MT300N-V2 running the Python stack
- [ ] Embedded firmware — C/C++ power management layer for battery-free operation

---

## Running Locally

### Backend
```bash
cd nodefree-py
pip install -r requirements.txt
python main.py
# API: http://localhost:8080
# Swagger docs: http://localhost:8080/docs
```

### Frontend
```bash
cd nodefree-ui
npm install
npm run dev
# UI: http://localhost:5173
```

### Production (single server)
```bash
cd nodefree-ui && npm run build
cd ../nodefree-py && python main.py
# Full app: http://localhost:8080
```

---

## Coding Standards

- Python: type hints on all functions, async wherever possible, no global mutable state
  except through Arc/Mutex patterns (use threading.Lock or asyncio.Lock)
- TypeScript: strict mode always on, no `any` types, all API responses cast through
  types.ts interfaces, props always explicitly typed
- No external cloud dependencies — everything runs on the local device
- Every new module gets a corresponding unit test file

---

## The Vision

The internet is infrastructure. Like roads, water, and electricity — it should belong to
the communities that use it. NodeFree is the device that makes that real.

One device. One windowsill. Free internet for your whole neighborhood. Forever.

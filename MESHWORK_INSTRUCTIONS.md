# Meshwork — Project Instructions for Windsurf

## Mission
Make internet access as free and universally available as air — owned by no one,
controlled by no one, and available to everyone.

Meshwork is an open-source, self-powered mesh networking device and software platform
that gives every person within 300 feet free community internet with zero monthly fee,
zero carrier, zero technical knowledge, and zero setup required.

---

## What We Are Building

A small physical device (target cost: ~$40) combined with an AI-powered software stack that:

1. Harvests ambient energy (RF, solar, thermal) to power itself — no outlet, no battery
2. Uses free, unlicensed TV White Space (TVWS) spectrum for legal broadband backhaul
3. Self-organizes into a neighborhood mesh network with neighboring Meshwork devices
4. Distributes free internet to all users in range automatically using AI-optimized routing
5. Requires zero configuration, zero accounts, and zero ongoing cost for end users

---

## Tech Stack

### Backend (Meshwork-py/)
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

### Embedded Firmware (Meshwork-firmware/)
- Language: C++ (Arduino-style) for bare-metal hardware control
- Targets: ESP32-S3, nRF9160, or GL.iNet GL-MT300N-V2
- Responsibility: Everything Python physically cannot do —
    - Ultra-low-power sleep/wake cycle management (every milliwatt matters)
    - Direct GPIO control for energy harvesting ICs (AEM10941, BQ25570) via I2C
    - Raw radio hardware initialization and TVWS spectrum scanning
    - Watchdog timers and hardware fault recovery
    - Boot sequence before the Python runtime is available
- Communicates with the Python layer via serial (UART) or local socket
- NOTE: C++ is used ONLY for hardware-level bare-metal operations that require
  direct register access and deterministic real-time execution. All higher-level
  logic, AI, networking, and API work stays in Python.

### Frontend (Meshwork-ui/)
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

## Language Responsibilities (Why Each Language)

| Language   | Layer                  | Why                                                        |
|------------|------------------------|------------------------------------------------------------|
| Python     | AI + API + Mesh logic  | Fast iteration, rich libraries, async, your strongest zone |
| C++        | Embedded firmware      | Bare-metal hardware control, real-time, <1MB memory budget |
| TypeScript | React dashboard UI     | Type-safe, strict, consistent with modern frontend standards|

---

## Architecture Principles

- **Fully decentralized** — no cloud server, no central authority, no single point of failure
- **Zero config** — every device must work out of the box with no user setup
- **AI-first routing** — the mesh brain scores gateways by latency (40%), bandwidth (35%),
  generosity score (15%), and signal strength (10%)
- **Graceful power degradation** — four power modes (FullOperation → Reduced → LowPower → Sleep)
  based on harvested milliwatts
- **Firmware/software boundary** — C++ owns the hardware, Python owns the intelligence.
  They communicate via a clean serial protocol. Neither crosses into the other's domain.
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

- [ ] TVWS radio driver (tvws.py) — Python interface to TVWS hardware for free spectrum backhaul
- [ ] Real batctl neighbor parsing — connect mesh.py scan_neighbors() to live hardware
- [ ] C++ firmware — power management, GPIO/I2C for energy harvesting IC, boot sequence
- [ ] Serial protocol — clean message format between C++ firmware and Python AI layer
- [ ] Energy harvesting IC reader — connect energy.py to AEM10941 or BQ25570 readings
- [ ] SQLite metrics logging — wire db.py log_metric() into the main heartbeat loop
- [ ] Dashboard authentication — protect the control panel from unauthorized access
- [ ] Hardware prototype — GL.iNet GL-MT300N-V2 running the Python stack
- [ ] Animated constellation map — pulse animations on ConstellationMap with live signal data

---

## Running Locally

### Backend
```bash
cd Meshwork-py
pip install -r requirements.txt
python main.py
# API: http://localhost:8080
# Swagger docs: http://localhost:8080/docs
```

### Frontend
```bash
cd Meshwork-ui
npm install
npm run dev
# UI: http://localhost:5173
```

### Production (single server)
```bash
cd Meshwork-ui && npm run build
cd ../Meshwork-py && python main.py
# Full app: http://localhost:8080
```

### Firmware (C++)
```bash
cd Meshwork-firmware
# Flash to target device using PlatformIO or Arduino IDE
pio run --target upload
```

---

## Coding Standards

- Python: type hints on all functions, async wherever possible, use asyncio.Lock for
  shared state, no bare except clauses
- TypeScript: strict mode always on, no `any` types, all API responses cast through
  types.ts interfaces, props always explicitly typed
- C++: minimize heap allocation, use fixed-size buffers, every ISR must be as short
  as possible, document every register write with a comment explaining why
- No external cloud dependencies — everything runs on the local device
- Every new module gets a corresponding unit test file

---

## The Vision

The internet is infrastructure. Like roads, water, and electricity — it should belong to
the communities that use it. Meshwork is the device that makes that real.

One device. One windowsill. Free internet for your whole neighborhood. Forever.

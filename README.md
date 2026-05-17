# Meshwork

> Make internet access as free and universally available as air — owned by no one, controlled by no one, and available to everyone.

---

## What Is Meshwork?

Meshwork is an open-source, self-powered mesh networking device and software platform that gives every person within 300 feet free community internet with:

- **Zero monthly fee** — no carrier, no subscription
- **Zero technical knowledge** — works out of the box
- **Zero setup** — plug in, it auto-configures
- **Zero ongoing cost** — powered by ambient energy (RF, solar, thermal)

A single $40 device on a windowsill harvests ambient energy, connects to free TV White Space spectrum for broadband backhaul, and self-organizes with neighboring Meshwork devices to blanket your neighborhood in free, community-owned internet.

---

## How It Works

### The Three-Layer Stack

Meshwork is deliberately split across three languages, each owning exactly one layer:

```
┌─────────────────────────────────────────┐
│  TypeScript + React 18                   │  ← Dashboard UI
│  (Type-safe, strict mode, Vite)          │     You see this
├─────────────────────────────────────────┤
│  Python 3.12 + FastAPI + Uvicorn         │  ← AI + API + Mesh Logic
│  (Async, SQLite, zero cloud deps)        │     The brain
├─────────────────────────────────────────┤
│  C++ (Arduino-style / PlatformIO)        │  ← Embedded Firmware
│  (ESP32-S3 / nRF9160 / GL.iNet)          │     The hardware
└─────────────────────────────────────────┘
                    ↑
              UART Serial
        JSON over 115200 baud
```

### Language Responsibilities

| Language | Layer | Why |
|----------|-------|-----|
| **C++** | Embedded firmware | Bare-metal hardware control, real-time execution, <1MB memory, direct register access |
| **Python** | AI + API + Mesh logic | Fast iteration, rich async libraries, gateway scoring, anomaly detection, REST API |
| **TypeScript** | React dashboard | Type-safe UI, strict mode, all API responses typed through shared interfaces |

**Architecture rule:** C++ owns the hardware. Python owns the intelligence. Neither crosses into the other's domain. They communicate through a clean, documented serial protocol.

---

## Architecture Blueprint

### 1. Firmware Layer (C++)

`nodefree-firmware/`

The firmware boots first, initializes all hardware, then runs a background loop:

```
Boot Sequence:
  1. Start UART serial (115200 baud)
  2. Initialize I2C bus (100 kHz)
  3. Probe for energy harvesting IC (AEM10941 → BQ25570 fallback)
  4. Configure MPPT (Maximum Power Point Tracking)
  5. Initialize TVWS radio module
  6. Scan for best unoccupied UHF channel
  7. Connect to TVWS backhaul
  8. Signal "ready" to Python layer

Main Loop (every 1-30 seconds):
  → Feed hardware watchdog (1s)
  → Read commands from Python (continuous)
  → Report power status: harvested mW, battery V, mode (5s)
  → Report radio status: freq, RSSI, throughput (10s)
  → Send heartbeat: uptime, neighbor count (30s)
  → Auto-transition power mode based on harvested energy
```

**Power Modes (graceful degradation):**

| Mode | Harvested | Behavior |
|------|-------------|----------|
| FullOperation | >500 mW | Everything on, max TX power, full routing |
| Reduced | 100–500 mW | 50% TX power, LED off, lower beacon rate |
| LowPower | 10–100 mW | Beacon only every 30s, no routing, no gateway |
| Sleep | <10 mW | Deep sleep, wake on I2C interrupt or RTC timer |

**Key files:**
- `src/main.cpp` — Boot sequence, main loop
- `src/power_manager.cpp` — I2C energy IC, sleep/wake, watchdog
- `src/radio_manager.cpp` — TVWS scan, channel selection, connect/disconnect
- `src/serial_protocol.cpp` — JSON message builder/parser
- `include/*.h` — Headers with register documentation

### 2. Backend Layer (Python)

`server/`

The Python layer is the intelligence — it never touches hardware directly. All sensor data arrives via the serial link from firmware.

```
FastAPI Server (port 8080)
  ├── /api/status              → Node health, power mode, uptime
  ├── /api/neighbors           → Live mesh neighbor list
  ├── /api/metrics/history     → 30-day contribution data
  ├── /api/set-gateway         → Toggle gateway mode (auth required)
  ├── /api/set-bandwidth-cap   → Set max bandwidth share (auth required)
  ├── /api/tvws/status         → TVWS backhaul link quality
  ├── /api/firmware/status     → Live firmware sensor readings
  └── /                        → Service health check

Mesh Loop (every 30 seconds, async):
  1. Scan for mesh neighbors (batctl or mock data)
  2. AI-rank gateways (latency 40%, bandwidth 35%, generosity 15%, signal 10%)
  3. Advertise as gateway if enabled and surplus bandwidth exists
  4. Route traffic through best gateway
  5. Detect anomalies in neighbor behavior
  6. Log metrics to SQLite (gb_shared, uptime_pct, is_gateway)
  7. Read power from serial link, determine power mode

Serial Link (background thread):
  → Reads newline-delimited JSON from firmware UART
  → Parses power, radio, heartbeat, alert, ready messages
  → Exposes latest readings to rest of Python stack
  → Simulation mode when no hardware present
```

**AI Module (`ai.py`):**
- `rank_gateways()` — Scores neighbors and picks optimal gateway
- `detect_anomalies()` — Flags unusual network behavior
- `predict_congestion()` — Forecasts bandwidth bottlenecks

**Key files:**
- `main.py` — Boot, runs API + mesh loop concurrently
- `api.py` — FastAPI routes, Pydantic models, auth, asyncio.Lock state
- `serial_link.py` — Thread-safe UART bridge to firmware
- `mesh.py` — Neighbor scanning, Node dataclass
- `ai.py` — Gateway scoring, anomaly detection
- `energy.py` — Power mode logic (reads from serial link)
- `tvws.py` — Python-side TVWS interface (mirrors firmware driver)
- `db.py` — SQLite metrics logging
- `auth.py` — Token-based dashboard authentication

**Authentication:**
- Token generated on first boot (SHA-256 hashed, stored locally)
- Displayed once in server console — save it
- Required for POST endpoints (gateway toggle, bandwidth cap)
- Persisted in browser localStorage
- `GET` endpoints remain public for mesh transparency

### 3. Frontend Layer (TypeScript)

`client/`

```
Dashboard (tabs)
  ├── Dashboard Tab
  │     ├── StatusCard      → Node health, neighbors, generosity, power mode
  │     └── MetricsChart    → 30-day contribution + gateway activity strip
  │
  ├── Network Tab
  │     ├── ConstellationMap → Animated HTML5 canvas mesh visualization
  │     │                        Signal rings, data packets on edges, live glow
  │     └── NeighborMap      → Neighbor list with signal, latency, generosity
  │
  └── Controls Tab
        ├── Gateway Mode      → Enable/disable with pressed-button UI
        ├── Bandwidth Cap     → Slider + apply
        └── Auth Gate         → Token login (shows when unauthenticated)
```

**Key files:**
- `src/App.tsx` — Tab layout, API polling every 10s
- `src/components/StatusCard.tsx` — Node health display
- `src/components/ConstellationMap.tsx` — Animated canvas mesh viz
- `src/components/MetricsChart.tsx` — Recharts line chart + activity strip
- `src/components/NeighborMap.tsx` — Neighbor list
- `src/components/Controls.tsx` — Gateway toggle, bandwidth cap, auth flow
- `src/types.ts` — Shared TypeScript interfaces (strict, no `any`)

---

## Serial Protocol (Firmware ↔ Python)

All communication is **newline-delimited JSON** over UART at **115200 baud**.

### Firmware → Python

```json
{"type":"power","harvested_mw":150.5,"battery_v":3.7,"mode":"Reduced"}
{"type":"radio","tvws_connected":true,"frequency_mhz":574.0,"rssi_dbm":-65.0}
{"type":"heartbeat","uptime_sec":3600,"neighbors":3}
{"type":"alert","code":"LOW_POWER","message":"Entering sleep mode"}
{"type":"ready","firmware_version":"0.1.0","hardware":"esp32s3"}
```

### Python → Firmware

```json
{"type":"cmd_gateway","enabled":true}
{"type":"cmd_power","mode":"FullOperation"}
{"type":"cmd_tvws","frequency_mhz":574.0,"bandwidth_mhz":6.0}
```

---

## File Structure

```
rf-dev/
├── README.md                          ← You are here
├── NODEFREE_INSTRUCTIONS.md           ← Original project instructions
│
├── server/                            ← Python backend
│   ├── main.py                        ← Boot + mesh loop
│   ├── api.py                         ← FastAPI routes
│   ├── serial_link.py                 ← UART bridge to firmware
│   ├── mesh.py                        ← Neighbor scanning
│   ├── ai.py                          ← Gateway scoring, anomaly detection
│   ├── energy.py                      ← Power mode logic
│   ├── tvws.py                        ← TVWS radio driver
│   ├── db.py                          ← SQLite metrics logging
│   ├── auth.py                        ← Token authentication
│   ├── requirements.txt               ← Python dependencies
│   └── tests/                         ← Unit tests
│       ├── test_energy.py
│       ├── test_mesh.py
│       ├── test_db.py
│       ├── test_ai.py
│       ├── test_tvws.py
│       ├── test_auth.py
│       ├── test_serial_link.py
│       └── test_firmware_protocol.py
│
├── client/                            ← React frontend
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.tsx                    ← Tab layout, API polling
│       ├── App.css                    ← Component styles
│       ├── index.css                  ← Global styles
│       ├── types.ts                   ← Shared interfaces
│       └── components/
│           ├── StatusCard.tsx
│           ├── ConstellationMap.tsx   ← Animated mesh viz
│           ├── MetricsChart.tsx
│           ├── NeighborMap.tsx
│           └── Controls.tsx           ← Auth + gateway controls
│
└── nodefree-firmware/                 ← C++ embedded firmware
    ├── platformio.ini                 ← Build targets (ESP32-S3, nRF9160)
    ├── include/
    │   ├── serial_protocol.h          ← Message format definition
    │   ├── power_manager.h            ← Energy IC + sleep/wake
    │   └── radio_manager.h            ← TVWS radio control
    └── src/
        ├── main.cpp                   ← Boot sequence + main loop
        ├── serial_protocol.cpp
        ├── power_manager.cpp
        └── radio_manager.cpp
```

---

## Running Locally

### Backend

```bash
cd server
pip install -r requirements.txt
python main.py
# API: http://localhost:8080
# Swagger docs: http://localhost:8080/docs
```

On first boot, a token is printed. Save it — shown only once.

### Frontend (development)

```bash
cd client
npm install
npm run dev
# UI: http://localhost:5173
```

### Frontend (production build)

```bash
cd client && npm run build
cd ../server && python main.py
# Full app: http://localhost:8080
```

### Firmware (ESP32-S3)

```bash
cd nodefree-firmware
# Install PlatformIO, then:
pio run --target upload
# Monitor: pio device monitor
```

---

## Coding Standards

- **Python:** Type hints on all functions, async wherever possible, `asyncio.Lock` for shared state, no bare `except` clauses, every module has a test file
- **TypeScript:** Strict mode always on, no `any` types, all API responses cast through `types.ts` interfaces, props always explicitly typed
- **C++:** Minimize heap allocation, use fixed-size buffers, every ISR must be as short as possible, document every register write with a comment explaining why
- **No external cloud dependencies** — everything runs on the local device

---

## The Vision

The internet is infrastructure. Like roads, water, and electricity — it should belong to the communities that use it. Meshwork is the device that makes that real.

**One device. One windowsill. Free internet for your whole neighborhood. Forever.**

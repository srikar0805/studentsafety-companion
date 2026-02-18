# 🛡️ Student Safety Companion

> **Campus Dispatch Copilot** — An AI-powered safety navigation system for university campuses. Get safe walking routes with real-time crime data analysis, emergency phone locations, and context-aware safety tips.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129-009688.svg)](https://fastapi.tiangolo.com)

---

## 📖 What It Does

Student Safety Companion helps university students and community members navigate campus safely by:

- **🗺️ Safe Route Planning** — Generates multiple walking routes between locations and ranks them by safety score
- **📊 Real-Time Risk Analysis** — Analyzes nearby crime incidents, patrol frequency, and safety infrastructure
- **🚨 Incident Awareness** — Displays crime data from MUPD, CPD, and police call logs on an interactive map
- **💡 Actionable Safety Tips** — Provides context-aware advice based on crime types in the area (e.g., "High theft area — keep valuables hidden")
- **🤖 AI Chat Assistant** — Natural language interface for asking about routes and safety via Archia-powered agents
- **📱 Mobile-Ready** — Responsive design optimized for on-the-go use

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│  Frontend (React + Vite + Leaflet)           │
│  Interactive map, route display, chat UI     │
└──────────────────┬───────────────────────────┘
                   │ HTTP / REST
┌──────────────────▼───────────────────────────┐
│  Backend (FastAPI)                            │
│  ├─ Route Generation (OSRM API)              │
│  ├─ Safety Analysis (Risk Scoring Engine)     │
│  ├─ Multi-Agent AI (Archia Cloud)            │
│  └─ Spatial Queries (PostGIS)                │
└──────────────────┬───────────────────────────┘
                   │ SQL
┌──────────────────▼───────────────────────────┐
│  PostgreSQL + PostGIS                        │
│  Crime incidents, police calls, CPD data,    │
│  shuttle stops, campus buildings, safety     │
│  assets (emergency phones, cameras, etc.)    │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend build |
| **PostgreSQL** | 14+ with **PostGIS** | Spatial database |
| **Git** | Any | Clone the repo |

### 1. Clone & Setup

```bash
git clone https://github.com/srikar0805/studentsafety-companion.git
cd studentsafety-companion
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required: PostgreSQL connection (local or Supabase)
DATABASE_URL=postgresql://postgres:password@localhost:5432/studentsafety

# Required for AI chat: Archia API key (https://archia.app)
ARCHIA_API_KEY=ask_xxxxxxxxxxxxxxxxx
```

> 💡 **Using Supabase?** Create a project at [supabase.com](https://supabase.com), go to Settings → Database, and copy the connection string. PostGIS is pre-enabled.

### 3. Install Backend Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary python-dotenv httpx polyline geopandas pandas sqlalchemy geoalchemy2 pydantic
```

### 4. Initialize Database

```bash
# Create tables and enable PostGIS
python scripts/init_db.py

# Load crime, shuttle, and safety data from CSV/GeoJSON files
python scripts/etl/load_data.py
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 6. Run the Application

Open **two terminals**:

**Terminal 1 — Backend (port 8000):**
```bash
uvicorn src.backend.app.main:app --reload --port 8000
```

**Terminal 2 — Frontend (port 5173):**
```bash
cd frontend
npm run dev
```

### 7. Open the App

Navigate to **http://localhost:5173** in your browser.

---

## 🗂️ Project Structure

```
studentsafety-companion/
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── components/        # UI components (Map, Chat, Controls)
│   │   ├── store/             # Zustand state management
│   │   └── App.tsx            # Root component
│   ├── package.json
│   └── vite.config.ts
│
├── src/backend/app/           # FastAPI backend
│   ├── main.py                # API endpoints (/api/routes, /api/dispatch)
│   ├── config.py              # Settings & env vars
│   ├── models.py              # Pydantic data models
│   ├── db.py                  # Database connection
│   ├── utils.py               # Utility functions
│   ├── tools.py               # Agent tool definitions
│   ├── services/
│   │   ├── queries.py         # PostGIS spatial queries
│   │   ├── safety.py          # Risk scoring algorithm
│   │   ├── ranking.py         # Route ranking engine
│   │   ├── osrm.py            # OSRM route generation
│   │   └── geocoding.py       # Location name → coordinates
│   ├── agents/                # AI agent implementations
│   │   ├── route_agent.py
│   │   ├── safety_agent.py
│   │   └── context_agent.py
│   ├── clients/
│   │   └── archia_client.py   # Archia AI API client
│   └── mcp/                   # Model Context Protocol endpoints
│
├── src/db/
│   └── schema.sql             # Database schema (PostGIS tables)
│
├── scripts/
│   ├── init_db.py             # Database initialization
│   └── etl/
│       └── load_data.py       # Data loading (CSV → PostgreSQL)
│
├── data/                      # Source data files
│   ├── crime_logs/            # MUPD & CPD incident CSVs
│   ├── shuttle_data/          # Shuttle stop locations
│   ├── campus_boundary/       # Campus GeoJSON boundary
│   └── traffic_stops/         # Traffic stop CSVs
│
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── design.md                  # Full system design document
└── LICENSE                    # MIT License
```

---

## 🔌 API Reference

### `POST /api/routes`

Generate safe walking routes between two locations.

**Request:**
```json
{
  "origin": "Student Center",
  "destination": "Jesse Hall",
  "priority": "safety",
  "user_mode": "student",
  "time": "current"
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "recommendation": {
    "routes": [
      {
        "rank": 1,
        "route": { "id": "route_0", "geometry": {...}, "distance_meters": 850 },
        "safety_analysis": { "risk_score": 15, "risk_level": "Very Safe", ... },
        "duration_minutes": 8,
        "safety_improvement_percent": 45,
        "explanation": "This route is rated Very Safe..."
      }
    ],
    "explanation": "I found 2 route(s) optimized for safety..."
  },
  "incidents": [...],
  "emergency_phones": [...]
}
```

### `POST /api/dispatch`

Chat with the AI assistant about campus safety.

**Request:**
```json
{
  "message": "Is it safe to walk to Ellis Library right now?"
}
```

### `GET /health`

Health check endpoint. Returns `{"status": "ok"}`.

---

## ⚙️ Configuration

All settings are configurable via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | PostgreSQL connection string |
| `ARCHIA_API_KEY` | *(optional)* | Archia AI API key for chat |
| `OSRM_BASE_URL` | `https://router.project-osrm.org` | Walking route engine |
| `SPATIAL_RADIUS_M` | `500` | Incident search radius (meters) |
| `PHONE_RADIUS_M` | `100` | Emergency phone search radius |
| `TEMPORAL_WINDOW_DAYS` | `30` | Incident lookback period (days) |
| `TRAFFIC_WINDOW_DAYS` | `90` | Traffic stop lookback (days) |

---

## 🧠 How the Safety Scoring Works

Each route is scored on a **0–100 risk scale** using this algorithm:

1. **Base Score** — 10 points per nearby incident
2. **Temporal Weight** — Recent incidents (< 30 days) count 5× more
3. **Time-of-Day** — Routes after 10 PM / before 6 AM have 2× risk
4. **Infrastructure** — Emergency phones reduce risk (−5 each, max −15)
5. **Patrol Frequency** — High patrol areas reduce risk (−10 points)

| Score | Risk Level |
|-------|------------|
| 0–20 | ✅ Very Safe |
| 21–40 | 🟢 Safe |
| 41–60 | 🟡 Moderate Risk |
| 61–80 | 🟠 Higher Risk |
| 81–100 | 🔴 High Risk |

---

## 🗃️ Database Tables

| Table | Records | Description |
|-------|---------|-------------|
| `crime_incidents` | ~1,700 | MUPD daily crime log |
| `cpd_incidents` | ~19,000 | Columbia PD ArcGIS data |
| `police_calls` | — | MUPD daily incident log |
| `traffic_stops` | — | CPD traffic stop data |
| `safety_assets` | ~2,500 | Emergency phones, cameras, blue lights |
| `shuttle_stops` | ~240 | Campus shuttle stop locations |
| `campus_buildings` | ~1,800 | Building footprints & names |
| `campus_boundary` | 1 | Campus perimeter polygon |

---

## 🧪 Testing

```bash
# Quick API test (backend must be running)
python test_api.py

# Run test suite
python -m pytest tests/

# Verify database has loaded data
python check_db_counts.py
```

---

## 📄 Additional Documents

| Document | Description |
|----------|-------------|
| [design.md](design.md) | Full system design with architecture diagrams, agent prompts, and API contracts |
| [ARCHIA_KEYS.md](ARCHIA_KEYS.md) | Guide for setting up Archia AI agent keys |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Integration guide for external services |
| [.env.example](.env.example) | Environment variable template with all options |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Copyright © 2026 Srikar

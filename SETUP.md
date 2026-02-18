# 🔧 Detailed Setup Guide

This guide walks through every step required to run Student Safety Companion locally.

---

## 1. Database Setup

### Option A: Local PostgreSQL

1. **Install PostgreSQL 14+** with the PostGIS extension:
   - **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/). During install, check the **Stack Builder** option and install PostGIS from there.
   - **macOS**: `brew install postgresql@14 postgis`
   - **Linux**: `sudo apt install postgresql postgis`

2. **Create the database**:
   ```bash
   psql -U postgres
   ```
   ```sql
   CREATE DATABASE studentsafety;
   \c studentsafety
   CREATE EXTENSION IF NOT EXISTS postgis;
   \q
   ```

3. **Set your connection string** in `.env`:
   ```
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/studentsafety
   ```

### Option B: Supabase (Cloud)

1. Create a free project at [supabase.com](https://supabase.com)
2. PostGIS is **pre-enabled** on Supabase
3. Go to **Settings → Database → Connection string** and copy the URI
4. Set it in `.env`:
   ```
   DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-1-us-east-1.pooler.supabase.com:6543/postgres
   ```

---

## 2. Initialize the Schema

This creates all tables (`crime_incidents`, `police_calls`, `cpd_incidents`, `safety_assets`, `shuttle_stops`, etc.) and spatial indexes:

```bash
python scripts/init_db.py
```

Expected output:
```
Connecting to database to apply schema...
Enabling PostGIS extension...
Applying schema from .../src/db/schema.sql...
Schema applied successfully.
```

---

## 3. Load Data

The ETL script reads CSV and GeoJSON files from the `data/` folder and inserts them into the database:

```bash
python scripts/etl/load_data.py
```

This loads:
- **Crime incidents** from `data/crime_logs/` (MUPD daily crime log)
- **CPD incidents** from `data/crime_logs/` (Columbia PD ArcGIS export)
- **Campus boundary** from `data/campus_boundary/`
- **Safety assets** (emergency phones, cameras) from campus data
- **Shuttle stops** from `data/shuttle_data/`

### Verify Data Loaded

```bash
python check_db_counts.py
```

Expected output (approximate):
```
crime_incidents: 1761
cpd_incidents: 19271
safety_assets: 2560
shuttle_stops: 241
campus_buildings: 1880
```

---

## 4. Backend Setup

### Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install core dependencies
pip install fastapi uvicorn psycopg2-binary python-dotenv httpx polyline pydantic

# For ETL scripts (if not already installed)
pip install pandas geopandas sqlalchemy geoalchemy2
```

### Start the Backend

```bash
uvicorn src.backend.app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

**Test it:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

---

## 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

> **Note:** Both the backend (port 8000) and frontend (port 5173) must be running simultaneously.

---

## 6. Using the App

### Map Interface

1. Open **http://localhost:5173** in your browser
2. The interactive map shows the University of Missouri campus
3. Use the map controls to zoom, pan, and toggle layers

### Route Planning

1. Enter an **origin** and **destination** (e.g., "Student Center" → "Jesse Hall")
2. Select your **priority**: Safety, Speed, or Balanced
3. Select your **mode**: Student or Community
4. The app generates multiple routes and displays them color-coded on the map
5. Each route shows a **safety score**, **incident count**, and **explanation**

### AI Chat

1. Click the chat button to open the AI assistant
2. Ask questions like:
   - "Is it safe to walk to Ellis Library at 11pm?"
   - "What's the safest route from Lathrop Hall to the Rec Center?"
   - "Are there any recent incidents near my route?"
3. The AI uses real crime data to provide contextual answers

---

## 7. Archia AI Setup (Optional)

The AI chat feature requires an [Archia](https://archia.app) API key:

1. Sign up at [archia.app](https://archia.app)
2. Create the following agents in your Archia dashboard:
   - **Campus Dispatch Orchestrator** — Main orchestrator agent
   - **Campus Routing Engine** — Route generation agent
   - **Campus risk and prediction engine** — Safety analysis agent
   - **campus context and journalism agent** — Context/RAG agent
3. Add your API key to `.env`:
   ```
   ARCHIA_API_KEY=ask_xxxxxxxxxxxxxxxxx
   ```
4. See [ARCHIA_KEYS.md](ARCHIA_KEYS.md) for detailed agent setup instructions

> **Note:** Route generation and safety analysis work **without** Archia. Only the `/api/dispatch` chat endpoint requires it.

---

## Troubleshooting

### "No incidents returned"
- Verify data is loaded: `python check_db_counts.py`
- Check that PostGIS extension is enabled: `SELECT PostGIS_version();` in psql

### "Connection refused" on port 8000
- Make sure the backend is running: `uvicorn src.backend.app.main:app --reload --port 8000`
- Check your `DATABASE_URL` in `.env`

### "CORS error" in browser console
- The backend allows all origins by default. If you changed the CORS config, ensure `localhost:5173` is allowed.

### Frontend shows blank map
- Make sure both backend and frontend are running
- Check browser console for errors
- Verify the backend returns data: `python test_api.py`

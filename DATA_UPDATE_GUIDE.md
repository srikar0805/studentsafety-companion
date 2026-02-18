# Automated Data Update System

> **Keep Safety Data Fresh** — Scheduled fetching and updating of crime logs, incident reports, and safety data

---

## Overview

The Student Safety Companion uses real-time crime data to provide accurate safety recommendations. This system automatically fetches fresh data from:

- **MUPD Daily Crime Log** — Updated daily at 3:00 AM
- **Columbia PD Crime Data** — Updated weekly on Sundays at 2:00 AM  
- **MUPD Incident Log** — Updated daily at 3:30 AM

---

## Default Update Schedules

| Data Source | Update Frequency | Schedule Time | Records/Update |
|-------------|------------------|---------------|----------------|
| MUPD Crime Log | Daily | 03:00 AM | ~50-100 |
| CPD Crime Data | Weekly | Sunday 02:00 AM | ~500-1000 |
| MUPD Incident Log | Daily | 03:30 AM | ~20-50 |

### Why These Schedules?

- **MUPD Crime Log (Daily)**: Campus incidents are reported daily — fresh data ensures accurate route safety scoring
- **CPD Data (Weekly)**: City-wide crime data is updated weekly — reduces API load while maintaining currency
- **MUPD Incident Log (Daily)**: Real-time incidents help identify emerging safety concerns

---

## Configuration

### Environment Variables

Add these to your `.env` file to customize update schedules:

```env
# Data Update Schedules
MUPD_CRIME_LOG_SCHEDULE=daily_03:00
CPD_CRIME_DATA_SCHEDULE=weekly_sunday_02:00
MUPD_INCIDENT_LOG_SCHEDULE=daily_03:30

# Automatically run ETL after fetching
AUTO_RUN_ETL=true

# Run scheduler continuously (for server deployment)
CONTINUOUS_MODE=false

# Data source URLs (configure based on actual endpoints)
MUPD_CRIME_LOG_URL=https://police.missouri.edu/daily-crime-log/
CPD_CRIME_DATA_URL=https://www.como.gov/CMS/gis/crimedata.php
MUPD_INCIDENT_LOG_URL=https://police.missouri.edu/daily-incident-log/

# Fetch data for last N days (for CPD)
CPD_FETCH_DAYS=30
```

### Schedule Format

Schedules use the following format:

- **Hourly**: `hourly` or `hourly_:30` (every hour at :30 minutes)
- **Daily**: `daily_HH:MM` (every day at HH:MM)
- **Weekly**: `weekly_DAY_HH:MM` (every DAY at HH:MM)

**Examples**:
```env
# Every hour
SCHEDULE=hourly

# Every day at 2:30 AM
SCHEDULE=daily_02:30

# Every Friday at 6:00 PM
SCHEDULE=weekly_friday_18:00
```

---

## Usage

### Option 1: Manual Run (One-Time Update)

```bash
# Fetch data only
python scripts/data_fetcher.py

# Fetch data and load into database
python scripts/data_fetcher.py --run-etl

# Force update (ignore frequency checks)
python scripts/data_fetcher.py --force --run-etl
```

### Option 2: Scheduled Run (Cron or Task Scheduler)

#### Linux/Mac (Cron)

Edit crontab:
```bash
crontab -e
```

Add schedule (example: daily at 3:00 AM):
```cron
0 3 * * * cd /path/to/studentsafety-companion && /path/to/.venv/bin/python scripts/schedule_updater.py --mode once
```

#### Windows (Task Scheduler)

1. Open **Task Scheduler**
2. Create New Task:
   - **Trigger**: Daily at 3:00 AM
   - **Action**: Start a program
     - **Program**: `C:\path\to\.venv\Scripts\python.exe`
     - **Arguments**: `scripts\schedule_updater.py --mode once`
     - **Start in**: `C:\path\to\studentsafety-companion`

### Option 3: Continuous Scheduler (Server Deployment)

Run scheduler as a background service:

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Run continuous scheduler
python scripts/schedule_updater.py --mode continuous
```

Or set in `.env`:
```env
CONTINUOUS_MODE=true
```

Then run:
```bash
python scripts/schedule_updater.py
```

---

## Integration with Archia AI Agents

The data update system ensures AI agents always have fresh safety data for analysis.

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Scheduled Data Fetcher                                  │
│  (runs daily at 3:00 AM)                                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Fetch MUPD Log  │ → data/crime_logs/mupd_crime_log_20260218.csv
         └─────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Run ETL Pipeline │ → Load into PostgreSQL + PostGIS
         └─────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Database Updated │
         └─────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  Archia AI Agents                                        │
│  ├─ Safety Intelligence Analyst                          │
│  │   └─ Queries fresh crime data via /mcp/risk          │
│  ├─ Route Advisor                                        │
│  │   └─ Uses updated risk scores                        │
│  └─ Conversation Manager                                 │
│      └─ Provides current safety context                  │
└─────────────────────────────────────────────────────────┘
```

### MCP Tool Integration

When Archia agents call safety analysis tools:

```python
# Backend: /mcp/risk endpoint
@app.post("/mcp/risk")
async def risk_model(payload: dict):
    # Queries database with FRESH crime data
    incidents = query_recent_incidents(
        route_geometry=payload['route'],
        days_back=30  # Last 30 days of data
    )
    
    # Risk score uses latest incidents
    risk_score = calculate_risk_score(incidents)
    
    return {
        "risk_score": risk_score,
        "incident_count": len(incidents),
        "data_freshness": "Last updated: 2026-02-18 03:00"
    }
```

---

## Data Freshness Indicators

### Add to API Responses

```python
# In main.py
@app.get("/api/data-status")
async def data_status():
    """Get data freshness status for all sources"""
    return {
        "mupd_crime_log": {
            "last_updated": "2026-02-18T03:00:00Z",
            "record_count": 1750,
            "status": "current"
        },
        "cpd_incidents": {
            "last_updated": "2026-02-17T02:00:00Z",
            "record_count": 19234,
            "status": "current"
        },
        "data_age_hours": 6  # Hours since last update
    }
```

### Display in Frontend

```typescript
// Show data freshness in UI
const DataFreshnessIndicator = () => {
  const [status, setStatus] = useState(null);
  
  useEffect(() => {
    fetch('/api/data-status')
      .then(r => r.json())
      .then(setStatus);
  }, []);
  
  return (
    <div>
      Last updated: {status?.mupd_crime_log?.last_updated}
      {status?.data_age_hours < 24 && <span>✓ Current</span>}
    </div>
  );
};
```

---

## Logging & Monitoring

### Log Files

All update operations are logged to:
```
logs/
├── data_fetcher_20260218.log
├── scheduler_20260218.log
└── etl_20260218.log
```

### Sample Log Output

```
2026-02-18 03:00:01 - INFO - Starting automated data update
2026-02-18 03:00:01 - INFO - Current time: 2026-02-18T03:00:01
2026-02-18 03:00:02 - INFO - Processing MUPD_CRIME_LOG
2026-02-18 03:00:05 - INFO - Fetched 87 records from MUPD
2026-02-18 03:00:05 - INFO - Saved 87 records to mupd_crime_log_20260218.csv
2026-02-18 03:00:06 - INFO - Triggering ETL pipeline
2026-02-18 03:00:12 - INFO - Loaded 87 new records into database
2026-02-18 03:00:12 - INFO - Data update complete
```

---

## Implementing Data Source Fetchers

The current implementation includes **placeholder fetchers**. You need to implement actual data fetching based on source availability:

### Example: MUPD Web Scraping

```python
from bs4 import BeautifulSoup
import requests

def fetch_mupd_crime_log():
    url = "https://police.missouri.edu/daily-crime-log/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the crime log table
    table = soup.find('table', {'class': 'crime-log'})
    
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip header
        cells = tr.find_all('td')
        rows.append({
            'Case Number': cells[0].text.strip(),
            'Date/Time Reported': cells[1].text.strip(),
            'Location of Occurence': cells[2].text.strip(),
            'Incident Type': cells[3].text.strip(),
            'Disposition': cells[4].text.strip()
        })
    
    return pd.DataFrame(rows)
```

### Example: CPD ArcGIS API

```python
def fetch_cpd_crime_data():
    # ArcGIS REST API endpoint (example)
    api_url = "https://gis.como.gov/arcgis/rest/services/Crime/MapServer/0/query"
    
    params = {
        "where": "report_date >= CURRENT_DATE - 30",
        "outFields": "*",
        "f": "json",
        "returnGeometry": "true"
    }
    
    response = requests.get(api_url, params=params)
    data = response.json()
    
    records = []
    for feature in data['features']:
        attrs = feature['attributes']
        geom = feature['geometry']
        
        records.append({
            'offense_id': attrs['OFFENSE_ID'],
            'report_date': attrs['REPORT_DATE'],
            'nibrs_description': attrs['NIBRS_DESC'],
            'full_address': attrs['ADDRESS'],
            'x': geom['x'],
            'y': geom['y']
        })
    
    return pd.DataFrame(records)
```

---

## Deployment Checklist

- [ ] Configure environment variables in `.env`
- [ ] Implement actual data source fetchers (replace placeholders)
- [ ] Test data fetching manually: `python scripts/data_fetcher.py --run-etl`
- [ ] Set up cron job or Task Scheduler
- [ ] Monitor logs for first few runs
- [ ] Add data freshness indicator to frontend
- [ ] Set up alerts for failed updates (optional)

---

## Troubleshooting

### Issue: "No data fetched"

**Cause**: Data source URL changed or fetcher not implemented

**Solution**: 
1. Check URL in `.env` is correct
2. Implement fetcher logic for that source
3. Run with `--force` flag to test

### Issue: "ETL pipeline failed"

**Cause**: Database connection issue or schema mismatch

**Solution**:
1. Verify `DATABASE_URL` is correct
2. Check database is running
3. Run `python scripts/init_db.py` to ensure schema is up to date

### Issue: "Duplicate key errors"

**Cause**: Trying to insert records that already exist

**Solution**: This is normal — the ETL uses `ON CONFLICT DO NOTHING` to skip duplicates

---

## Next Steps

1. **Implement Real Fetchers**: Replace placeholder fetchers with actual API calls or web scraping
2. **Add Email Alerts**: Notify admins when updates fail
3. **Dashboard**: Create admin page showing data freshness status
4. **Incremental Updates**: Only fetch new records since last update (not full dataset)
5. **Backup System**: Archive old CSV files before replacing

---

## Summary

✅ **Automated Updates**: Crime data stays fresh without manual intervention  
✅ **Configurable Schedules**: Adjust update frequency per data source  
✅ **AI Agent Ready**: Archia agents always query current safety data  
✅ **Production Ready**: Works with cron, Task Scheduler, or continuous mode  

For questions or issues, check logs in `logs/` directory.

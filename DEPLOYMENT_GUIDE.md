# Deployment Guide - Student Safety Companion

This guide covers deploying your full-stack application to production with separate hosting for frontend, backend, and database.

## 🏗️ Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Frontend      │ ───► │    Backend       │ ───► │   PostgreSQL    │
│   (Vercel)      │      │   (Railway)      │      │   + PostGIS     │
│   React + Vite  │      │   FastAPI        │      │   (Railway)     │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

---

## 📋 Prerequisites

- GitHub account (for deployment automation)
- Vercel account (for frontend)
- Railway account (for backend + database)
- Archia API key
- OSRM instance or use public demo server

---

## 1️⃣ Database Deployment (Railway)

### Step 1: Create PostgreSQL Database

1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"** → **"Provision PostgreSQL"**
3. Wait for database to provision

### Step 2: Enable PostGIS Extension

1. In Railway dashboard, click your PostgreSQL service
2. Go to **"Connect"** tab → copy the connection URL
3. Use a PostgreSQL client (like DBeaver or psql) to connect:
   ```bash
   psql "<your-railway-database-url>"
   ```
4. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

### Step 3: Run Schema Migration

From your local machine:
```bash
# Export Railway database URL
$env:DATABASE_URL="<your-railway-database-url>"

# Run schema
python -c "from src.backend.app.db import get_db_connection; conn = get_db_connection(); cursor = conn.cursor(); cursor.execute(open('src/db/schema.sql').read()); cursor.execute(open('src/db/schema_update_locations.sql').read()); conn.commit(); print('✓ Schema created'); cursor.close(); conn.close()"

# Load campus data
python scripts/etl/load_campus_locations.py
```

### Step 4: Save Database Credentials

Copy the following from Railway:
- `DATABASE_URL` (full connection string)

---

## 2️⃣ Backend Deployment (Railway)

### Step 1: Prepare Backend for Deployment

Create `Procfile` in project root:
```bash
web: uvicorn src.backend.app.main:app --host 0.0.0.0 --port $PORT
```

Create `railway.json` in project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.backend.app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Update `requirements.txt` to include all dependencies:
```txt
fastapi
uvicorn[standard]
psycopg2-binary
requests
python-dotenv
pydantic
pydantic-settings
```

### Step 2: Deploy to Railway

1. In Railway dashboard, click **"New Project"** → **"Deploy from GitHub repo"**
2. Connect your GitHub account and select your repository
3. Railway will auto-detect Python and deploy

### Step 3: Set Environment Variables

In Railway dashboard → **"Variables"** tab, add:

```bash
DATABASE_URL=<from-postgresql-service>
ARCHIA_API_KEY=<your-archia-key>
OSRM_BASE_URL=https://router.project-osrm.org
GEOCODER_BASE_URL=https://nominatim.openstreetmap.org
GEOCODER_USER_AGENT=StudentSafetyCompanion/1.0
```

### Step 4: Get Backend URL

- Railway will provide a URL like `https://your-app.railway.app`
- Copy this URL for frontend configuration

---

## 3️⃣ Frontend Deployment (Vercel)

### Step 1: Prepare Frontend Build

Create `vercel.json` in `frontend/` directory:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install"
}
```

Update `frontend/.env.production`:
```bash
VITE_API_URL=https://your-backend.railway.app
```

### Step 2: Deploy to Vercel

**Option A: Vercel CLI (Recommended)**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

**Option B: Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Set **Root Directory** to `frontend`
5. Set **Build Command** to `npm run build`
6. Set **Output Directory** to `dist`
7. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.railway.app`
8. Click **"Deploy"**

### Step 3: Configure CORS

After deployment, update your backend's `main.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend to Railway (it auto-deploys on git push).

---

## 4️⃣ Alternative: Deploy Everything to Railway

If you prefer a single platform:

### Step 1: Create Railway Project
```bash
railway login
railway init
```

### Step 2: Add PostgreSQL
```bash
railway add postgresql
```

### Step 3: Configure Services

Create `railway.toml`:
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt && cd frontend && npm install && npm run build"

[deploy]
startCommand = "uvicorn src.backend.app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

### Step 4: Set Environment Variables
```bash
railway variables set ARCHIA_API_KEY=<your-key>
railway variables set OSRM_BASE_URL=https://router.project-osrm.org
```

### Step 5: Deploy
```bash
railway up
```

---

## 5️⃣ Alternative: Render.com Deployment

### Backend (Render)

1. Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: studentsafety-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.backend.app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: studentsafety-db
          property: connectionString
      - key: ARCHIA_API_KEY
        sync: false
      - key: OSRM_BASE_URL
        value: https://router.project-osrm.org

databases:
  - name: studentsafety-db
    databaseName: studentsafety
    user: studentsafety
    postgresMajorVersion: 15
```

2. Connect GitHub repo to Render
3. Render auto-deploys on push

### Frontend (Render Static Site)

1. Add `frontend` as separate static site
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Add environment variable: `VITE_API_URL`

---

## 6️⃣ Environment Variables Summary

### Backend Variables
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
ARCHIA_API_KEY=your_archia_api_key_here
OSRM_BASE_URL=https://router.project-osrm.org
GEOCODER_BASE_URL=https://nominatim.openstreetmap.org
GEOCODER_USER_AGENT=StudentSafetyCompanion/1.0
SPATIAL_RADIUS_M=100
TEMPORAL_WINDOW_DAYS=30
MAX_ROUTE_ALTERNATIVES=3
```

### Frontend Variables
```bash
VITE_API_URL=https://your-backend-url.com
```

---

## 7️⃣ Post-Deployment Checklist

- [ ] Database schema deployed with PostGIS
- [ ] Campus locations data loaded (376 buildings)
- [ ] Backend health check passes: `curl https://your-backend.com/health`
- [ ] Frontend loads and connects to backend
- [ ] Test API endpoints:
  - `/api/routes`
  - `/api/dispatch`
  - `/api/news`
  - `/api/shuttles`
- [ ] Test disambiguation flow ("take me to a dorm")
- [ ] Test transportation modes (walk/bike/car)
- [ ] CORS configured for your frontend domain
- [ ] SSL certificates active (automatic with Vercel/Railway)

---

## 8️⃣ Monitoring & Logs

### Railway Logs
```bash
railway logs
```

### Vercel Logs
- Dashboard → Your Project → Deployments → View Function Logs

### Database Monitoring
- Railway dashboard shows connection count, query stats
- Set up alerts for high CPU/memory usage

---

## 9️⃣ Custom Domain (Optional)

### Vercel (Frontend)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as shown

### Railway (Backend)
1. Go to Settings → Domains
2. Add custom domain
3. Update DNS CNAME record

---

## 🚀 Quick Deploy Commands

**Deploy Backend (Railway):**
```bash
cd studentsafety-companion
git add .
git commit -m "Deploy backend"
git push origin main
# Railway auto-deploys
```

**Deploy Frontend (Vercel):**
```bash
cd frontend
vercel --prod
```

---

## ⚠️ Common Issues

### Issue: CORS errors
**Fix**: Add your frontend URL to `allow_origins` in `main.py`

### Issue: Database connection fails
**Fix**: Ensure DATABASE_URL includes `?sslmode=require` for Railway

### Issue: PostGIS functions fail
**Fix**: Run `CREATE EXTENSION postgis;` in database

### Issue: Build fails on Railway
**Fix**: Ensure `requirements.txt` is in project root

### Issue: Frontend can't reach backend
**Fix**: Check `VITE_API_URL` matches your backend Railway URL

---

## 📊 Estimated Costs

| Service | Free Tier | Paid Plan |
|---------|-----------|-----------|
| **Vercel** | Unlimited personal projects | $20/month Pro |
| **Railway** | $5/month free credit | Pay as you go (~$10-20/month) |
| **Render** | Free tier available | $7/month starter |

**Recommended**: Start with Vercel (frontend) + Railway (backend + DB) = ~$15/month

---

## 🎯 Production Optimizations

1. **Enable caching** for static routes
2. **Add rate limiting** to API endpoints
3. **Set up CDN** for faster global access
4. **Enable compression** (gzip) for API responses
5. **Add monitoring** (Sentry, LogRocket)
6. **Database connection pooling** for better performance

---

## 📞 Support

If you encounter deployment issues:
- Railway: https://railway.app/help
- Vercel: https://vercel.com/support
- Render: https://render.com/docs

---

## ✅ You're Live!

Your Student Safety Companion is now deployed and accessible worldwide! 🎉

**Frontend URL**: `https://your-app.vercel.app`  
**Backend URL**: `https://your-backend.railway.app`  
**Health Check**: `https://your-backend.railway.app/health`

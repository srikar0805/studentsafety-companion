# Archia Console: How to Find Connection Keys

This guide explains what to look for in the Archia console to populate [src/backend/.env](src/backend/.env).

## What you need

- Postgres/PostGIS connection string (or host, port, user, password, db name)
- Redis endpoint and password (if available)
- Geocoding service base URL and API key (if Archia provides it)
- Routing service base URL and API key (if Archia provides it)

## Where to look in Archia

Exact menu names can vary, but these are the most common paths in hosted consoles:

1. Log in to https://console.archia.app/
2. Go to the project or workspace for this app
3. Look for one of these sections (pick the closest match):
   - Services
   - Resources
   - Databases
   - Networking
   - Secrets / Credentials
   - Integrations

## Postgres/PostGIS

1. Open the database service details
2. Find a connection string or individual fields like:
   - Host, Port, User, Password, Database
   - SSL mode or CA certificate info
3. Map to .env:
   - DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME

## Redis

1. Open the Redis (cache) service details
2. Find endpoint and password
3. Map to .env:
   - REDIS_URL=redis://:PASSWORD@HOST:PORT/0
   - If SSL is required, it may be: rediss://:PASSWORD@HOST:PORT/0

## Geocoding (optional)

If Archia provides a geocoding service:

1. Open the geocoding service details
2. Find base URL and API key or token
3. Map to .env:
   - GEOCODER_BASE_URL=https://<geocoder-base-url>
   - GEOCODER_USER_AGENT=campus-dispatch-copilot/1.0
   - If a key is required, share it and I will add a GEOCODER_API_KEY setting

## Routing (optional)

If Archia provides routing:

1. Open the routing service details
2. Find base URL and API key or token
3. Map to .env:
   - OSRM_BASE_URL=https://<routing-base-url>
   - If a key is required, share it and I will add an OSRM_API_KEY setting

## Alternative (without Archia)

If you want to run everything without Archia, you can use local or public services instead:

### Postgres/PostGIS (local)

1. Install PostgreSQL and PostGIS locally.
2. Create a database named `campus_safety`.
3. Update .env:
   - DATABASE_URL=postgresql://postgres:postgres@localhost:5432/campus_safety

### Redis (local)

1. Install Redis locally.
2. Update .env:
   - REDIS_URL=redis://localhost:6379/0

### Geocoding (public)

Use Nominatim (no key required):

- GEOCODER_BASE_URL=https://nominatim.openstreetmap.org
- GEOCODER_USER_AGENT=campus-dispatch-copilot/1.0

### Routing (public)

Use the public OSRM demo server:

- OSRM_BASE_URL=https://router.project-osrm.org

Note: Public services have rate limits. For production, use paid or self-hosted services.

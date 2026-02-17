import uuid
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    Coordinates, LineString, RouteRequest, RoutesResponse, Recommendation,
)
from .services.geocoding import geocode_location, GeocodingError
from .services.osrm import generate_routes, OsrmError
from .services.safety import analyze_route_safety, patrol_frequency_label
from .services.ranking import rank_routes, build_ranked_routes
from .services.queries import (
    fetch_incidents,
    fetch_traffic_stop_count,
    fetch_emergency_phones,
)
from .agents.route_agent import RouteAgent
from .agents.safety_agent import SafetyAgent
from .agents.context_agent import ContextAgent
from .db import get_conn
from .config import settings
from .clients.archia_client import call_archia
from .utils import parse_request_time

logger = logging.getLogger("campus_dispatch")

app = FastAPI(title="Campus Dispatch Copilot API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize local agents (used by MCP endpoints)
route_agent = RouteAgent()
safety_agent = SafetyAgent()
context_agent = ContextAgent()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _resolve_coords(value) -> Coordinates:
    """Resolve a string location name or dict/Coordinates to Coordinates."""
    if isinstance(value, str):
        return geocode_location(value)
    if isinstance(value, dict):
        return Coordinates(**value)
    return value


def _generate_route_pipeline(
    origin: Coordinates,
    destination: Coordinates,
    priority: str,
    user_mode: str,
    time_str: str,
) -> dict:
    """
    Full local route generation pipeline:
    1. OSRM route generation
    2. Safety analysis per route (DB queries)
    3. Ranking
    4. Build RankedRoute objects
    """
    try:
        current_time = parse_request_time(time_str)
    except Exception:
        current_time = datetime.now(timezone.utc)

    # 1. Generate route alternatives via OSRM
    routes = generate_routes(origin, destination)

    # 2. Safety analysis for each route
    all_incidents = []
    all_phones = []
    analyses = []

    for route in routes:
        try:
            incidents = fetch_incidents(
                route.geometry,
                radius_m=settings.spatial_radius_m,
                days_back=settings.temporal_window_days,
            )
        except Exception:
            logger.exception("Incident fetch failed for route %s", route.id)
            incidents = []

        try:
            traffic_stops = fetch_traffic_stop_count(
                route.geometry,
                radius_m=settings.spatial_radius_m,
                days_back=settings.traffic_window_days,
            )
        except Exception:
            traffic_stops = 0

        try:
            phones = fetch_emergency_phones(
                route.geometry,
                radius_m=settings.phone_radius_m,
            )
        except Exception:
            phones = []

        patrol = patrol_frequency_label(traffic_stops)
        analysis = analyze_route_safety(
            incidents=incidents,
            emergency_phones=len(phones),
            lighting_quality="moderate",
            patrol_frequency=patrol,
            user_mode=user_mode,
            current_time=current_time,
        )

        analyses.append(analysis)
        all_incidents.extend(incidents)
        all_phones.extend(phones)

    # 3. Rank routes
    ranked_indices = rank_routes(routes, analyses, priority, current_time.hour)

    # 4. Build RankedRoute objects
    ranked_routes = build_ranked_routes(routes, analyses, ranked_indices)

    # 5. Build explanation
    if ranked_routes:
        best = ranked_routes[0]
        explanation = (
            f"I found {len(ranked_routes)} route(s) optimized for {priority}. "
            f"The recommended route is {best.route.id} — "
            f"{best.explanation}"
        )
    else:
        explanation = "No routes could be generated."

    # De-duplicate incidents by id
    seen_ids: set[str] = set()
    unique_incidents = []
    for inc in all_incidents:
        if inc.id not in seen_ids:
            seen_ids.add(inc.id)
            unique_incidents.append(inc)

    # De-duplicate phones
    unique_phones = list({(p.latitude, p.longitude): p for p in all_phones}.values())

    return {
        "ranked_routes": ranked_routes,
        "incidents": unique_incidents,
        "emergency_phones": unique_phones,
        "explanation": explanation,
    }


# ---------------------------------------------------------------------------
# Main route endpoint — uses LOCAL pipeline for real routes
# ---------------------------------------------------------------------------
@app.post("/api/routes")
async def api_routes(request: RouteRequest):
    """
    Generate real routes using OSRM + safety analysis + ranking.
    Returns structured RoutesResponse for the frontend map.
    """
    try:
        origin = _resolve_coords(request.origin)
        destination = _resolve_coords(request.destination)
    except GeocodingError as e:
        raise HTTPException(status_code=400, detail=f"Could not geocode location: {e}")

    try:
        result = _generate_route_pipeline(
            origin=origin,
            destination=destination,
            priority=request.priority,
            user_mode=request.user_mode,
            time_str=request.time,
        )
    except OsrmError as e:
        raise HTTPException(status_code=502, detail=f"Routing service error: {e}")
    except Exception as e:
        logger.exception("Route pipeline error")
        raise HTTPException(status_code=500, detail=f"Route generation error: {e}")

    ranked_routes = result["ranked_routes"]

    recommendation = Recommendation(
        routes=ranked_routes,
        primary_recommendation=ranked_routes[0],
        explanation=result["explanation"],
        comparison=(
            f"Comparing {len(ranked_routes)} routes based on {request.priority} priority."
            if ranked_routes
            else ""
        ),
    )

    try:
        resp = RoutesResponse(
            request_id=str(uuid.uuid4()),
            recommendation=recommendation,
            incidents=result["incidents"],
            emergency_phones=result["emergency_phones"],
        )
        return resp.model_dump(mode="json")
    except Exception as e:
        logger.exception("Response serialization error")
        raise HTTPException(status_code=500, detail=f"Serialization error: {e}")


# ---------------------------------------------------------------------------
# Chat/dispatch endpoint — Archia AI for conversational response
# ---------------------------------------------------------------------------
@app.post("/api/dispatch")
@app.post("/api/v1/dispatch")
async def dispatch(req: Request):
    data = await req.json()
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    try:
        result = call_archia(message)
        return {"response": result.get("output", "")}
    except Exception as e:
        logger.exception("Dispatch error")
        raise HTTPException(status_code=500, detail=f"Dispatch error: {e}")


# ---------------------------------------------------------------------------
# MCP tool endpoints (called by Archia agents as external tools)
# ---------------------------------------------------------------------------
@app.post("/mcp/route")
async def mcp_route(payload: dict):
    origin_raw = payload.get("origin") or payload.get("start_location") or payload.get("from")
    dest_raw = payload.get("destination") or payload.get("end_location") or payload.get("to")

    if not origin_raw or not dest_raw:
        return {"error": "Missing origin or destination"}

    try:
        if isinstance(origin_raw, str):
            origin = geocode_location(origin_raw)
        else:
            origin = Coordinates(**origin_raw)

        if isinstance(dest_raw, str):
            dest = geocode_location(dest_raw)
        else:
            dest = Coordinates(**dest_raw)
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}

    return await route_agent.run({
        "origin_coords": origin.model_dump(),
        "destination_coords": dest.model_dump(),
        "priority": payload.get("priority", "balanced"),
    })


@app.post("/mcp/risk")
async def mcp_risk(payload: dict):
    routes = payload.get("routes", [])
    if not routes:
        return {"results": []}

    return await safety_agent.run({
        "routes": routes,
        "time": payload.get("time", "current"),
        "mode": payload.get("mode", "student"),
    })


@app.post("/mcp/shuttle")
async def mcp_shuttle(payload: dict):
    loc_raw = payload.get("location")
    if not loc_raw:
        return {"error": "Missing location"}

    try:
        if isinstance(loc_raw, str):
            loc = geocode_location(loc_raw)
        else:
            loc = Coordinates(**loc_raw)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT stop_name, ST_Distance(location_geo, ST_SetSRID(ST_MakePoint(%s, %s), 4326), true) as dist
            FROM shuttle_stops
            WHERE ST_DWithin(location_geo, ST_SetSRID(ST_MakePoint(%s, %s), 4326), 500)
            ORDER BY dist ASC
            LIMIT 3;
        """, (loc.longitude, loc.latitude, loc.longitude, loc.latitude))

        stops = [{"name": row[0], "distance_meters": row[1]} for row in cur.fetchall()]
        cur.close()
        conn.close()

        return {"nearby_stops": stops}
    except Exception as e:
        return {"error": str(e)}


@app.post("/mcp/traffic")
async def mcp_traffic(payload: dict):
    routes = payload.get("routes", [])
    results = []

    for r in routes:
        try:
            geom = LineString(**r["geometry"])
            count = fetch_traffic_stop_count(geom, settings.spatial_radius_m, settings.traffic_window_days)
            results.append({"route_id": r.get("id") or r.get("route_id"), "traffic_stops": count})
        except Exception:
            results.append({"route_id": r.get("id") or r.get("route_id"), "traffic_stops": 0})

    return {"results": results}


@app.post("/mcp/rag")
async def mcp_rag(payload: dict):
    routes = payload.get("routes", [])
    return await context_agent.run({"routes": routes})


@app.get("/health")
def health():
    return {"status": "ok"}

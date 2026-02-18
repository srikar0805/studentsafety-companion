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
from .services.locations import is_category_query, get_locations_by_category
from .schemas.agent_schemas import AgentDisambiguationResponse, LocationOption
from .utils import parse_request_time

logger = logging.getLogger("campus_dispatch")

app = FastAPI(title="Campus Dispatch Copilot API")

# CORS for frontend
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
    transportation_mode: str = "foot",
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
    from .models import TransportationMode as TM
    try:
        mode = TM(transportation_mode)
    except ValueError:
        mode = TM.WALK
    routes = generate_routes(origin, destination, mode=mode)

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
            route_length_m=route.distance_meters,
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
            transportation_mode=request.transportation_mode.value if hasattr(request.transportation_mode, 'value') else str(request.transportation_mode),
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
    """
    Conversational dispatch endpoint.

    Flow:
      1. Check if the message is a category query (dorm, library, etc.)
         - If yes, return disambiguation options from local DB
      2. Otherwise, forward to Archia AI for conversational routing
    """
    data = await req.json()
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    # ── Step 1: Local disambiguation check ──────────────────────
    is_category, category = is_category_query(message)
    if is_category and category:
        locations = get_locations_by_category(category, limit=10)

        if len(locations) > 1:
            # Multiple options — ask the user to pick
            category_labels = {
                "dorm": "dorm",
                "library": "library",
                "dining": "dining hall",
                "academic": "academic building",
                "recreation": "recreation facility",
                "parking": "parking location",
            }
            label = category_labels.get(category, category)

            options = [
                LocationOption(
                    name=loc.name,
                    address=loc.address,
                    coordinates=loc.coordinates,
                    category=loc.category,
                    distance_meters=None,
                )
                for loc in locations
            ]

            return AgentDisambiguationResponse(
                category=category,
                question=f"Which {label} would you like to go to?",
                options=options,
            ).model_dump()

        elif len(locations) == 1:
            # Single match — skip disambiguation, route via Archia
            loc = locations[0]
            message = f"Take me to {loc.name}"
            logger.info(f"Single {category} match, routing directly to {loc.name}")

        # else: no locations found, fall through to Archia

    # ── Step 2: Forward to Archia AI ────────────────────────────
    try:
        result = call_archia(message)

        # Extract response - Archia returns {"output": response_data}
        response_data = result.get("output", "")

        if isinstance(response_data, str):
            return {"response": response_data}

        if isinstance(response_data, dict):
            return response_data

        return {"response": str(response_data)}

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
        "transportation_mode": payload.get("transportation_mode", "foot"),
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


# ---------------------------------------------------------------------------
# News endpoints — local safety news with NLP classification
# ---------------------------------------------------------------------------
@app.get("/api/news")
def api_news():
    """Get classified, sentiment-scored local safety news articles."""
    from .services.news_service import get_news_articles
    return get_news_articles()


@app.get("/api/news/sentiment")
def api_news_sentiment():
    """Get aggregated sentiment statistics."""
    from .services.news_service import get_news_sentiment
    return get_news_sentiment()


# ---------------------------------------------------------------------------
# Shuttle endpoints — routes, stops, and live positions
# ---------------------------------------------------------------------------
@app.get("/api/shuttles")
def api_shuttle_positions():
    """Get current shuttle positions (live or simulated)."""
    from .services.shuttle_service import get_shuttle_positions
    return get_shuttle_positions()


@app.get("/api/shuttles/routes")
def api_shuttle_routes():
    """Get all shuttle routes with geometry."""
    from .services.shuttle_service import get_shuttle_routes
    return get_shuttle_routes()


@app.get("/api/shuttles/stops")
def api_shuttle_stops():
    """Get all shuttle stop locations."""
    from .services.shuttle_service import get_shuttle_stops
    return get_shuttle_stops()

# ---------------------------------------------------------------------------
# Risk Grid / Heatmap endpoints
# ---------------------------------------------------------------------------
@app.get("/api/risk-zones")
def api_risk_zones(time: int = None):
    """Get crime risk grid as GeoJSON. Optionally specify hour (0-23)."""
    from .services.risk_grid_service import generate_risk_grid
    return generate_risk_grid(hour=time)


# ---------------------------------------------------------------------------
# Infrastructure endpoints
# ---------------------------------------------------------------------------
@app.get("/api/infrastructure")
def api_infrastructure():
    """Get traffic infrastructure (signals, crosswalks, streetlights)."""
    from .services.infrastructure_service import get_infrastructure
    return get_infrastructure()


@app.get("/api/traffic-signals")
def api_traffic_signals():
    """Get real traffic signal locations for Columbia MO from OpenStreetMap."""
    from .services.infrastructure_service import get_traffic_signals
    return get_traffic_signals()


# ---------------------------------------------------------------------------
# Reverse geocoding endpoint
# ---------------------------------------------------------------------------
@app.get("/api/geocode/reverse")
def api_reverse_geocode(lat: float, lon: float):
    """Reverse geocode lat/lon to a place name."""
    # Try campus buildings table first
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT name FROM campus_buildings
            WHERE ST_DWithin(
                geometry,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                50
            )
            ORDER BY ST_Distance(
                geometry,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            )
            LIMIT 1
        """, (lon, lat, lon, lat))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {"display_name": row[0], "source": "campus_buildings"}
    except Exception:
        pass

    # Fall back to Nominatim
    try:
        import requests
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 18},
            headers={"User-Agent": "StudentSafetyCompanion/1.0"},
            timeout=3,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "display_name": data.get("display_name", f"{lat:.4f}, {lon:.4f}"),
                "source": "nominatim",
            }
    except Exception:
        pass

    return {"display_name": f"{lat:.4f}, {lon:.4f}", "source": "coordinates"}


# ---------------------------------------------------------------------------
# Route comparison endpoint (fast vs safe)
# ---------------------------------------------------------------------------
@app.post("/api/routes/compare")
async def api_route_compare(request: RouteRequest):
    """Compare fast vs safe route side by side."""
    try:
        origin = _resolve_coords(request.origin)
        destination = _resolve_coords(request.destination)
    except GeocodingError as e:
        raise HTTPException(status_code=400, detail=f"Could not geocode: {e}")

    try:
        fast_result = _generate_route_pipeline(
            origin=origin, destination=destination,
            priority="speed", user_mode=request.user_mode,
            time_str=request.time,
        )
        safe_result = _generate_route_pipeline(
            origin=origin, destination=destination,
            priority="safety", user_mode=request.user_mode,
            time_str=request.time,
        )
    except Exception as e:
        logger.exception("Route comparison error")
        raise HTTPException(status_code=500, detail=str(e))

    fast_route = fast_result["ranked_routes"][0] if fast_result["ranked_routes"] else None
    safe_route = safe_result["ranked_routes"][0] if safe_result["ranked_routes"] else None

    comparison = {}
    if fast_route and safe_route:
        fast_score = fast_route.safety_analysis.risk_score
        safe_score = safe_route.safety_analysis.risk_score
        if fast_score > 0:
            safer_pct = round(((fast_score - safe_score) / fast_score) * 100)
        else:
            safer_pct = 0
        time_diff = safe_route.duration_minutes - fast_route.duration_minutes
        comparison = {
            "safer_percentage": max(0, safer_pct),
            "time_tradeoff_minutes": max(0, time_diff),
            "recommendation": "safe" if safer_pct > 15 else "fast",
        }

    return {
        "fast": fast_route.model_dump(mode="json") if fast_route else None,
        "safe": safe_route.model_dump(mode="json") if safe_route else None,
        "comparison": comparison,
    }




# ---------------------------------------------------------------------------
# CoMo Transit endpoints — public transit routes, stops, and schedules
# ---------------------------------------------------------------------------
@app.get("/api/transit/routes")
def api_transit_routes():
    """Get all CoMo Transit fixed routes."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, route_number, route_name, route_color, route_description, is_active
            FROM transit_routes
            WHERE is_active = TRUE
            ORDER BY route_number;
        """)
        
        routes = []
        for row in cur.fetchall():
            routes.append({
                "id": row[0],
                "route_number": row[1],
                "route_name": row[2],
                "route_color": row[3],
                "route_description": row[4],
                "is_active": row[5],
            })
        
        cur.close()
        conn.close()
        return {"routes": routes}
    except Exception as e:
        logger.exception("Transit routes fetch error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transit/routes/{route_id}")
def api_transit_route_detail(route_id: int):
    """Get detailed information for a specific route."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Get route info
        cur.execute("""
            SELECT id, route_number, route_name, route_color, route_description, is_active
            FROM transit_routes
            WHERE id = %s;
        """, (route_id,))
        
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Route not found")
        
        route = {
            "id": row[0],
            "route_number": row[1],
            "route_name": row[2],
            "route_color": row[3],
            "route_description": row[4],
            "is_active": row[5],
        }
        
        cur.close()
        conn.close()
        return route
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Transit route detail fetch error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transit/routes/{route_id}/stops")
def api_transit_route_stops(route_id: int):
    """Get all stops for a specific route."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, route_id, stop_code, stop_name, stop_sequence, 
                   ST_Y(location_geo::geometry) as latitude, 
                   ST_X(location_geo::geometry) as longitude,
                   is_timepoint
            FROM transit_stops
            WHERE route_id = %s
            ORDER BY stop_sequence;
        """, (route_id,))
        
        stops = []
        for row in cur.fetchall():
            stops.append({
                "id": row[0],
                "route_id": row[1],
                "stop_code": row[2],
                "stop_name": row[3],
                "stop_sequence": row[4],
                "latitude": row[5],
                "longitude": row[6],
                "is_timepoint": row[7],
            })
        
        cur.close()
        conn.close()
        return {"stops": stops}
    except Exception as e:
        logger.exception("Transit stops fetch error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transit/routes/{route_id}/schedule")
def api_transit_route_schedule(route_id: int, service_type: str = "weekday"):
    """Get schedule for a specific route and service type."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                ts.id,
                ts.stop_code,
                ts.stop_name,
                ts.stop_sequence,
                sch.departure_time,
                sch.is_last_stop,
                sch.service_type
            FROM transit_schedules sch
            JOIN transit_stops ts ON ts.id = sch.stop_id
            WHERE sch.route_id = %s 
              AND sch.service_type = %s
            ORDER BY sch.departure_time, ts.stop_sequence;
        """, (route_id, service_type))
        
        schedule_entries = []
        for row in cur.fetchall():
            schedule_entries.append({
                "stop_id": row[0],
                "stop_code": row[1],
                "stop_name": row[2],
                "stop_sequence": row[3],
                "departure_time": str(row[4]),
                "is_last_stop": row[5],
                "service_type": row[6],
            })
        
        cur.close()
        conn.close()
        return {"schedule": schedule_entries, "service_type": service_type}
    except Exception as e:
        logger.exception("Transit schedule fetch error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transit/stops/nearest")
def api_transit_nearest_stops(lat: float, lon: float, limit: int = 5):
    """Find nearest transit stops to a location."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                ts.id,
                ts.stop_name,
                ts.stop_code,
                tr.route_name,
                tr.route_color,
                ST_Distance(
                    ts.location_geo, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_meters,
                ST_Y(ts.location_geo::geometry) as latitude,
                ST_X(ts.location_geo::geometry) as longitude
            FROM transit_stops ts
            JOIN transit_routes tr ON tr.id = ts.route_id
            WHERE ts.location_geo IS NOT NULL
            ORDER BY distance_meters ASC
            LIMIT %s;
        """, (lon, lat, limit))
        
        stops = []
        for row in cur.fetchall():
            stops.append({
                "id": row[0],
                "stop_name": row[1],
                "stop_code": row[2],
                "route_name": row[3],
                "route_color": row[4],
                "distance_meters": round(row[5], 2),
                "latitude": row[6],
                "longitude": row[7],
            })
        
        cur.close()
        conn.close()
        return {"stops": stops}
    except Exception as e:
        logger.exception("Nearest transit stops fetch error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


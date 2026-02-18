"""
Shuttle Service.

Provides shuttle routes, stops, and live/simulated positions
from the Go COMO Transit ETA SPOT API and PostGIS database.
"""

import logging
import math
import random
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ETA SPOT API config
API_URL = "https://gocomotransit.etaspot.net/service.php"
TOKEN = "TESTING"


def _fetch_from_etaspot(service: str) -> Optional[Dict]:
    """Fetch data from ETA SPOT API."""
    try:
        import requests
        resp = requests.get(API_URL, params={"service": service, "token": TOKEN}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"ETA SPOT API ({service}) failed: {e}")
        return None


def _get_routes_from_db() -> List[Dict]:
    """Load shuttle routes from PostGIS database."""
    try:
        from ..db import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT route_id, route_name, color,
                   ST_AsGeoJSON(geometry)::json as geojson
            FROM shuttle_routes
            WHERE is_active = TRUE
            ORDER BY route_id
        """)
        routes = []
        for row in cur.fetchall():
            routes.append({
                "route_id": row[0],
                "name": row[1],
                "color": row[2] or "#3b82f6",
                "geometry": row[3],
            })
        cur.close()
        conn.close()
        return routes
    except Exception as e:
        logger.warning(f"DB route fetch failed: {e}")
        return []


def _get_stops_from_db() -> List[Dict]:
    """Load shuttle stops from PostGIS database."""
    try:
        from ..db import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT stop_id, stop_name,
                   ST_Y(location_geo::geometry) as lat,
                   ST_X(location_geo::geometry) as lon
            FROM shuttle_stops
            ORDER BY stop_name
        """)
        stops = []
        for row in cur.fetchall():
            stops.append({
                "stop_id": row[0],
                "name": row[1],
                "lat": row[2],
                "lon": row[3],
            })
        cur.close()
        conn.close()
        return stops
    except Exception as e:
        logger.warning(f"DB stops fetch failed: {e}")
        return []


# ─── Fallback Data ─────────────────────────────────────────────

FALLBACK_ROUTES = [
    {
        "route_id": 405,
        "name": "Black Route",
        "color": "#1a1a1a",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-92.3277, 38.9404], [-92.3290, 38.9420], [-92.3310, 38.9440],
                [-92.3340, 38.9460], [-92.3360, 38.9470], [-92.3380, 38.9450],
                [-92.3370, 38.9430], [-92.3340, 38.9410], [-92.3310, 38.9400],
                [-92.3277, 38.9404],
            ]
        },
    },
    {
        "route_id": 406,
        "name": "Gold Route",
        "color": "#F1B82D",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-92.3266, 38.9446], [-92.3250, 38.9460], [-92.3230, 38.9480],
                [-92.3210, 38.9490], [-92.3200, 38.9470], [-92.3220, 38.9450],
                [-92.3240, 38.9440], [-92.3266, 38.9446],
            ]
        },
    },
    {
        "route_id": 407,
        "name": "Silver Route",
        "color": "#94a3b8",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-92.3300, 38.9380], [-92.3320, 38.9370], [-92.3350, 38.9360],
                [-92.3380, 38.9355], [-92.3400, 38.9370], [-92.3390, 38.9390],
                [-92.3360, 38.9400], [-92.3330, 38.9395], [-92.3300, 38.9380],
            ]
        },
    },
]

FALLBACK_STOPS = [
    {"stop_id": 1, "name": "Memorial Union", "lat": 38.9465, "lon": -92.3275},
    {"stop_id": 2, "name": "Jesse Hall", "lat": 38.9438, "lon": -92.3268},
    {"stop_id": 3, "name": "Rec Center", "lat": 38.9380, "lon": -92.3300},
    {"stop_id": 4, "name": "Engineering", "lat": 38.9470, "lon": -92.3310},
    {"stop_id": 5, "name": "Greek Town", "lat": 38.9395, "lon": -92.3310},
    {"stop_id": 6, "name": "Hospital", "lat": 38.9384, "lon": -92.3283},
    {"stop_id": 7, "name": "Library", "lat": 38.9448, "lon": -92.3266},
    {"stop_id": 8, "name": "Stadium", "lat": 38.9355, "lon": -92.3390},
    {"stop_id": 9, "name": "Student Center", "lat": 38.9480, "lon": -92.3280},
    {"stop_id": 10, "name": "Providence Road", "lat": 38.9465, "lon": -92.3390},
]


def _simulate_position(route_coords: list, route_id: int) -> dict:
    """Simulate a shuttle position along a route."""
    now = datetime.now()
    # Use time + route_id to make each shuttle move independently
    t = ((now.timestamp() / 60) + route_id * 7) % len(route_coords)
    idx = int(t) % len(route_coords)
    next_idx = (idx + 1) % len(route_coords)
    frac = t - int(t)

    lon = route_coords[idx][0] + frac * (route_coords[next_idx][0] - route_coords[idx][0])
    lat = route_coords[idx][1] + frac * (route_coords[next_idx][1] - route_coords[idx][1])

    # Calculate heading
    dx = route_coords[next_idx][0] - route_coords[idx][0]
    dy = route_coords[next_idx][1] - route_coords[idx][1]
    heading = math.degrees(math.atan2(dy, dx))

    return {"lat": lat, "lon": lon, "heading": heading}


# ─── Public API ───────────────────────────────────────────────

def get_shuttle_routes() -> List[Dict]:
    """Get all shuttle routes with geometry."""
    # Try API first
    data = _fetch_from_etaspot("get_routes")
    if data and "get_routes" in data:
        routes = []
        for r in data["get_routes"]:
            enc = r.get("encLine")
            coords = []
            if enc:
                try:
                    import polyline
                    decoded = polyline.decode(enc)
                    coords = [[lon, lat] for lat, lon in decoded]
                except Exception:
                    pass
            routes.append({
                "route_id": r.get("id"),
                "name": r.get("name"),
                "color": f"#{r.get('color', '3b82f6')}",
                "geometry": {"type": "LineString", "coordinates": coords} if coords else None,
            })
        if routes:
            return [r for r in routes if r["geometry"]]

    # Try DB
    db_routes = _get_routes_from_db()
    if db_routes:
        return db_routes

    return FALLBACK_ROUTES


def get_shuttle_stops() -> List[Dict]:
    """Get all shuttle stops."""
    data = _fetch_from_etaspot("get_stops")
    if data and "get_stops" in data:
        stops = []
        for s in data["get_stops"]:
            stops.append({
                "stop_id": s.get("id"),
                "name": s.get("name"),
                "lat": s.get("lat"),
                "lon": s.get("lng"),
            })
        if stops:
            return stops

    # Try DB
    db_stops = _get_stops_from_db()
    if db_stops:
        return db_stops

    return FALLBACK_STOPS


def get_shuttle_positions() -> List[Dict]:
    """Get current shuttle positions (API or simulated)."""
    # Try live API positions
    data = _fetch_from_etaspot("get_vehicles")
    if data and "get_vehicles" in data:
        vehicles = []
        for v in data["get_vehicles"]:
            vehicles.append({
                "vehicle_id": v.get("equipmentID", ""),
                "route_id": v.get("routeID"),
                "lat": v.get("lat"),
                "lon": v.get("lng"),
                "heading": v.get("heading", 0),
                "speed": v.get("speed", 0),
            })
        if vehicles:
            return vehicles

    # Simulate positions along fallback routes
    routes = get_shuttle_routes()
    positions = []
    for route in routes:
        coords = route.get("geometry", {}).get("coordinates", [])
        if coords:
            pos = _simulate_position(coords, route["route_id"])
            positions.append({
                "vehicle_id": f"sim-{route['route_id']}",
                "route_id": route["route_id"],
                "route_name": route["name"],
                "route_color": route.get("color", "#3b82f6"),
                **pos,
                "speed": random.randint(5, 15),
            })

    return positions

"""
Infrastructure Service.

Provides traffic infrastructure data (signals, crosswalks, streetlights)
from the PostGIS database or hardcoded defaults.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def _fetch_from_db() -> List[Dict]:
    """Load infrastructure features from osm_infrastructure table."""
    try:
        from ..db import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT feature_type,
                   ST_Y(geometry::geometry) as lat,
                   ST_X(geometry::geometry) as lon,
                   properties
            FROM osm_infrastructure
            WHERE feature_type IN ('traffic_signal', 'crosswalk', 'streetlight_zone')
            ORDER BY feature_type
        """)
        features = []
        for row in cur.fetchall():
            features.append({
                "type": row[0],
                "lat": row[1],
                "lon": row[2],
                "properties": row[3] or {},
            })
        cur.close()
        conn.close()
        return features
    except Exception as e:
        logger.warning(f"Infrastructure DB fetch failed: {e}")
        return []


# Fallback campus infrastructure
FALLBACK_INFRASTRUCTURE = [
    # Traffic signals
    {"type": "traffic_signal", "lat": 38.9465, "lon": -92.3275, "properties": {"name": "Memorial Union & Rollins"}},
    {"type": "traffic_signal", "lat": 38.9438, "lon": -92.3268, "properties": {"name": "Jesse Hall & Hitt St"}},
    {"type": "traffic_signal", "lat": 38.9404, "lon": -92.3277, "properties": {"name": "University Ave & College Ave"}},
    {"type": "traffic_signal", "lat": 38.9510, "lon": -92.3220, "properties": {"name": "Broadway & Providence"}},
    {"type": "traffic_signal", "lat": 38.9380, "lon": -92.3300, "properties": {"name": "Stadium & Providence"}},
    {"type": "traffic_signal", "lat": 38.9470, "lon": -92.3380, "properties": {"name": "College & Providence"}},

    # Crosswalks
    {"type": "crosswalk", "lat": 38.9448, "lon": -92.3266, "properties": {"name": "Library Crosswalk"}},
    {"type": "crosswalk", "lat": 38.9460, "lon": -92.3280, "properties": {"name": "Memorial Union Crosswalk"}},
    {"type": "crosswalk", "lat": 38.9430, "lon": -92.3260, "properties": {"name": "Hitt St Crosswalk"}},
    {"type": "crosswalk", "lat": 38.9395, "lon": -92.3310, "properties": {"name": "Greek Town Crosswalk"}},
    {"type": "crosswalk", "lat": 38.9384, "lon": -92.3283, "properties": {"name": "Hospital Crosswalk"}},
    {"type": "crosswalk", "lat": 38.9490, "lon": -92.3290, "properties": {"name": "Engineering Crosswalk"}},

    # Streetlight zones (higher density lit areas)
    {"type": "streetlight_zone", "lat": 38.9440, "lon": -92.3270, "properties": {"name": "Jesse Hall Lit Zone", "radius": 100}},
    {"type": "streetlight_zone", "lat": 38.9465, "lon": -92.3275, "properties": {"name": "Memorial Union Lit Zone", "radius": 120}},
    {"type": "streetlight_zone", "lat": 38.9380, "lon": -92.3300, "properties": {"name": "Rec Center Lit Zone", "radius": 80}},
    {"type": "streetlight_zone", "lat": 38.9470, "lon": -92.3315, "properties": {"name": "Engineering Lit Zone", "radius": 90}},
    {"type": "streetlight_zone", "lat": 38.9510, "lon": -92.3230, "properties": {"name": "Downtown Lit Zone", "radius": 150}},
]


def get_infrastructure() -> List[Dict]:
    """Get all infrastructure features."""
    features = _fetch_from_db()
    if features:
        return features
    return FALLBACK_INFRASTRUCTURE


def get_traffic_signals() -> List[Dict]:
    """
    Fetch traffic signal locations for Columbia MO from OpenStreetMap Overpass API.
    Caches results in memory for 1 hour.
    Falls back to DB (osm_infrastructure) or hardcoded data.
    """
    import time
    import requests as _requests

    # Simple in-memory cache
    cache_key = "_traffic_signals_cache"
    cache_ts_key = "_traffic_signals_ts"
    cache_ttl = 3600  # 1 hour

    cached = getattr(get_traffic_signals, cache_key, None)
    cached_ts = getattr(get_traffic_signals, cache_ts_key, 0)

    if cached and (time.time() - cached_ts) < cache_ttl:
        return cached

    # Try Overpass API for Columbia MO area
    try:
        overpass_query = (
            '[out:json][timeout:15];'
            'node["highway"="traffic_signals"](38.90,-92.40,38.98,-92.25);'
            'out body;'
        )
        resp = _requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": overpass_query},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        signals = []
        for el in data.get("elements", []):
            name = el.get("tags", {}).get("name", "")
            cross_street = el.get("tags", {}).get("cross_street", "")
            label = name or cross_street or f"Signal #{el['id']}"
            signals.append({
                "id": el["id"],
                "lat": el["lat"],
                "lon": el["lon"],
                "name": label,
            })

        if signals:
            setattr(get_traffic_signals, cache_key, signals)
            setattr(get_traffic_signals, cache_ts_key, time.time())
            logger.info(f"Loaded {len(signals)} traffic signals from Overpass API")
            return signals
    except Exception as e:
        logger.warning(f"Overpass API failed: {e}")

    # Fallback: extract traffic_signal entries from existing infrastructure
    all_infra = get_infrastructure()
    signals = [
        {"id": i, "lat": f["lat"], "lon": f["lon"], "name": f["properties"].get("name", f"Signal {i}")}
        for i, f in enumerate(all_infra)
        if f["type"] == "traffic_signal"
    ]
    setattr(get_traffic_signals, cache_key, signals)
    setattr(get_traffic_signals, cache_ts_key, time.time())
    return signals


def get_lighting_score(lat: float, lon: float, radius: float = 0.002) -> float:
    """
    Calculate a lighting/infrastructure score for a given location.
    Returns 0.0 (poor) to 1.0 (well-lit).
    """
    features = get_infrastructure()
    score = 0.0

    for f in features:
        dist = ((f["lat"] - lat) ** 2 + (f["lon"] - lon) ** 2) ** 0.5
        if dist < radius:
            if f["type"] == "streetlight_zone":
                score += 0.4
            elif f["type"] == "traffic_signal":
                score += 0.2
            elif f["type"] == "crosswalk":
                score += 0.1

    return min(score, 1.0)

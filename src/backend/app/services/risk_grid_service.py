"""
Risk Grid Service.

Generates a spatial risk grid over Columbia, MO campus area
based on crime data, severity weights, and time-of-day distribution.
"""

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

# Campus bounds (Columbia, MO)
MIN_LAT, MAX_LAT = 38.930, 38.955
MIN_LON, MAX_LON = -92.345, -92.315
GRID_SIZE = 0.002  # ~200m cells

# Crime severity weights
SEVERITY_WEIGHTS = {
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
}

# Night hours are higher risk
HOUR_RISK_MULTIPLIER = {
    **{h: 1.0 for h in range(6, 18)},    # Day (6am-6pm)
    **{h: 1.5 for h in range(18, 21)},    # Evening (6pm-9pm)
    **{h: 2.0 for h in range(21, 24)},    # Night (9pm-12am)
    **{h: 2.0 for h in range(0, 6)},      # Late night (12am-6am)
}


def _fetch_incidents_from_db() -> List[Dict]:
    """Fetch all incidents from all crime tables."""
    try:
        from ..db import get_conn
        conn = get_conn()
        cur = conn.cursor()

        # Union across all crime tables
        cur.execute("""
            SELECT lat, lon, severity, hour FROM (
                SELECT
                    ST_Y(location_geo::geometry) as lat,
                    ST_X(location_geo::geometry) as lon,
                    CASE
                        WHEN incident_type ILIKE '%%assault%%' OR incident_type ILIKE '%%robbery%%' THEN 'high'
                        WHEN incident_type ILIKE '%%theft%%' OR incident_type ILIKE '%%burglary%%' THEN 'medium'
                        ELSE 'low'
                    END as severity,
                    EXTRACT(HOUR FROM date_occurred) as hour
                FROM crime_incidents
                WHERE location_geo IS NOT NULL

                UNION ALL

                SELECT
                    ST_Y(location_geo::geometry) as lat,
                    ST_X(location_geo::geometry) as lon,
                    CASE
                        WHEN nibrs_description ILIKE '%%assault%%' OR nibrs_description ILIKE '%%robbery%%' THEN 'high'
                        WHEN nibrs_description ILIKE '%%theft%%' OR nibrs_description ILIKE '%%larceny%%' THEN 'medium'
                        ELSE 'low'
                    END as severity,
                    EXTRACT(HOUR FROM report_date) as hour
                FROM cpd_incidents
                WHERE location_geo IS NOT NULL

                UNION ALL

                SELECT
                    ST_Y(location_geo::geometry) as lat,
                    ST_X(location_geo::geometry) as lon,
                    'low' as severity,
                    EXTRACT(HOUR FROM call_time) as hour
                FROM police_calls
                WHERE location_geo IS NOT NULL
            ) AS all_incidents
        """)

        incidents = []
        for row in cur.fetchall():
            incidents.append({
                "lat": row[0], "lon": row[1],
                "severity": row[2], "hour": int(row[3]) if row[3] is not None else 12,
            })
        cur.close()
        conn.close()
        return incidents
    except Exception as e:
        logger.warning(f"DB incident fetch for risk grid failed: {e}")
        return []


# Hardcoded incident hotspots for fallback
FALLBACK_INCIDENTS = [
    {"lat": 38.9382, "lon": -92.3300, "severity": "high", "hour": 23},
    {"lat": 38.9385, "lon": -92.3305, "severity": "high", "hour": 1},
    {"lat": 38.9395, "lon": -92.3310, "severity": "high", "hour": 22},
    {"lat": 38.9400, "lon": -92.3315, "severity": "medium", "hour": 21},
    {"lat": 38.9410, "lon": -92.3260, "severity": "medium", "hour": 0},
    {"lat": 38.9430, "lon": -92.3280, "severity": "low", "hour": 14},
    {"lat": 38.9440, "lon": -92.3270, "severity": "low", "hour": 11},
    {"lat": 38.9355, "lon": -92.3390, "severity": "medium", "hour": 23},
    {"lat": 38.9360, "lon": -92.3385, "severity": "high", "hour": 2},
    {"lat": 38.9470, "lon": -92.3320, "severity": "low", "hour": 15},
    {"lat": 38.9510, "lon": -92.3220, "severity": "medium", "hour": 20},
    {"lat": 38.9515, "lon": -92.3230, "severity": "high", "hour": 22},
    {"lat": 38.9380, "lon": -92.3280, "severity": "medium", "hour": 19},
    {"lat": 38.9445, "lon": -92.3268, "severity": "low", "hour": 9},
    {"lat": 38.9404, "lon": -92.3277, "severity": "low", "hour": 16},
]


def generate_risk_grid(hour: int = None) -> Dict:
    """
    Generate a GeoJSON FeatureCollection of risk cells.

    Args:
        hour: Hour of day (0-23). If None, uses current hour.

    Returns:
        GeoJSON FeatureCollection with risk scores per cell.
    """
    if hour is None:
        hour = datetime.now().hour

    incidents = _fetch_incidents_from_db()
    if not incidents:
        incidents = FALLBACK_INCIDENTS

    hour_mult = HOUR_RISK_MULTIPLIER.get(hour, 1.0)

    # Generate grid cells
    features = []
    lat = MIN_LAT
    while lat < MAX_LAT:
        lon = MIN_LON
        while lon < MAX_LON:
            # Count incidents in this cell
            cell_score = 0.0
            for inc in incidents:
                if lat <= inc["lat"] < lat + GRID_SIZE and lon <= inc["lon"] < lon + GRID_SIZE:
                    weight = SEVERITY_WEIGHTS.get(inc["severity"], 1.0)
                    # Boost if incident happened around similar hour
                    hour_diff = abs(inc["hour"] - hour)
                    if hour_diff > 12:
                        hour_diff = 24 - hour_diff
                    temporal_boost = 1.0 + (1.0 if hour_diff <= 3 else 0.0)
                    cell_score += weight * temporal_boost

            if cell_score > 0:
                # Normalize to 0-1 range (cap at 10)
                normalized = min(cell_score * hour_mult / 10.0, 1.0)
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon + GRID_SIZE / 2, lat + GRID_SIZE / 2],
                    },
                    "properties": {
                        "risk_score": round(normalized, 3),
                        "incident_count": int(cell_score / max(SEVERITY_WEIGHTS.values())),
                    },
                })

            lon += GRID_SIZE
        lat += GRID_SIZE

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "hour": hour,
            "total_cells": len(features),
            "grid_size_degrees": GRID_SIZE,
        },
    }

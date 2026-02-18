from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from ..db import get_conn
from ..models import Coordinates, Incident, LineString
from ..utils import linestring_to_wkt, normalize_incident_type


def is_within_campus(point: Coordinates) -> bool:
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM campus_boundary
            WHERE ST_Contains(
                geometry::geometry,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
        )
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (point.longitude, point.latitude))
            return bool(cur.fetchone()[0])


def fetch_incidents(route: LineString, radius_m: int, days_back: int) -> list[Incident]:

    wkt = linestring_to_wkt(route)
    cutoff = datetime.utcnow() - timedelta(days=days_back)

    query = """
        WITH route AS (
            SELECT ST_GeogFromText(%s) AS geom
        )
        SELECT id::text AS id,
               incident_type AS type,
               date_occurred AS date,
               location_name AS description,
               NULL AS severity,
               ST_Y(location_geo::geometry) AS lat,
               ST_X(location_geo::geometry) AS lon
        FROM crime_incidents, route
        WHERE location_geo IS NOT NULL
          AND date_occurred IS NOT NULL
          AND date_occurred >= %s
          AND ST_DWithin(location_geo, route.geom, %s)
        UNION ALL
        SELECT offense_id::text AS id,
               nibrs_description AS type,
               report_date AS date,
               nibrs_description AS description,
               NULL AS severity,
               ST_Y(location_geo::geometry) AS lat,
               ST_X(location_geo::geometry) AS lon
        FROM cpd_incidents, route
        WHERE location_geo IS NOT NULL
          AND report_date IS NOT NULL
          AND report_date >= %s
          AND ST_DWithin(location_geo, route.geom, %s)
        UNION ALL
        SELECT incident_number::text AS id,
               incident_type AS type,
               call_time AS date,
               description,
               NULL AS severity,
               ST_Y(location_geo::geometry) AS lat,
               ST_X(location_geo::geometry) AS lon
        FROM police_calls, route
        WHERE location_geo IS NOT NULL
          AND call_time IS NOT NULL
          AND call_time >= %s
          AND ST_DWithin(location_geo, route.geom, %s)
    """

    incidents: list[Incident] = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    query,
                    (
                        wkt,
                        cutoff,
                        radius_m,
                        cutoff,
                        radius_m,
                        cutoff,
                        radius_m,
                    ),
                )
                rows = cur.fetchall()
                
                for row in rows:
                    incident_id, incident_type, date, description, severity, lat, lon = row
                    incidents.append(
                        Incident(
                            id=str(incident_id),
                            type=normalize_incident_type(incident_type),
                            location=Coordinates(latitude=lat, longitude=lon),
                            date=date,
                            description=description or "",
                            severity=severity or "medium",
                        )
                    )
            except Exception as e:
                raise e
    return incidents


def fetch_traffic_stop_count(route: LineString, radius_m: int, days_back: int) -> int:
    wkt = linestring_to_wkt(route)
    cutoff = datetime.utcnow() - timedelta(days=days_back)

    query = """
        WITH route AS (
            SELECT ST_GeogFromText(%s) AS geom
        )
        SELECT COUNT(*)
        FROM traffic_stops, route
        WHERE location_geo IS NOT NULL
          AND stop_date IS NOT NULL
          AND stop_date >= %s
          AND ST_DWithin(location_geo, route.geom, %s)
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (wkt, cutoff, radius_m))
            return int(cur.fetchone()[0])


def fetch_emergency_phones(route: LineString, radius_m: int) -> list[Coordinates]:
    wkt = linestring_to_wkt(route)

    query = """
        WITH route AS (
            SELECT ST_GeogFromText(%s) AS geom
        )
        SELECT ST_Y(location_geo::geometry) AS lat,
               ST_X(location_geo::geometry) AS lon
        FROM safety_assets, route
        WHERE location_geo IS NOT NULL
          AND asset_type ILIKE 'Emergency Phone%'
          AND ST_DWithin(location_geo, route.geom, %s)
    """

    phones: list[Coordinates] = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (wkt, radius_m))
            for row in cur.fetchall():
                lat, lon = row
                phones.append(Coordinates(latitude=lat, longitude=lon))
    return phones

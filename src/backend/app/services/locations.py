"""
Location service for campus location queries and disambiguation.

Lookup priority:
  1. campus_locations table (seeded from campus_buildings)
  2. campus_buildings table (name search via ILIKE)
  3. Nominatim geocoding (online fallback, biased to Mizzou campus)
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from ..db import get_db_connection
from ..models import CampusLocation, LocationCategory, Coordinates
from .geocoding import geocode_location, GeocodingError

logger = logging.getLogger("campus_dispatch")

# Common category keywords for detection
CATEGORY_KEYWORDS = {
    "dorm": ["dorm", "dorms", "residence hall", "residence", "housing"],
    "library": ["library", "libraries"],
    "dining": ["dining", "food", "cafeteria", "restaurant", "cafe", "eat"],
    "academic": ["academic", "classroom", "lecture hall", "department"],
    "recreation": ["gym", "recreation", "rec", "fitness", "sports"],
    "parking": ["parking", "garage", "lot"],
}


def is_category_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if a query is asking for a category of locations rather than a specific place.
    
    Returns:
        (is_category, category_name) tuple
    """
    query_lower = query.lower()
    
    # Check for explicit category patterns
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # Match patterns like "take me to a dorm", "find me food", "where's a library"
            if keyword in query_lower:
                return (True, category)
    
    return (False, None)


def get_locations_by_category(category: str, limit: int = 10) -> List[CampusLocation]:
    """
    Fetch all active locations in a specific category.

    Lookup priority:
      1. campus_locations table (seeded, categorized)
      2. campus_buildings table (name-based keyword search fallback)

    Args:
        category: The LocationCategory value (e.g., "dorm", "library")
        limit: Maximum number of results to return

    Returns:
        List of CampusLocation objects
    """
    # --- Tier 1: campus_locations table ---
    locations = _category_from_campus_locations(category, limit)
    if locations:
        return locations

    # --- Tier 2: campus_buildings name-based keyword search ---
    logger.info(f"No results in campus_locations for '{category}', trying campus_buildings")
    return _category_from_campus_buildings(category, limit)


# Keyword patterns for searching campus_buildings by name when campus_locations is empty
_BUILDING_NAME_KEYWORDS: dict[str, list[str]] = {
    "dorm": ["%HALL%", "%RESIDENCE%", "%DORM%"],
    "library": ["%LIBRARY%"],
    "dining": ["%DINING%", "%CAFE%", "%UNION%", "%STUDENT CENTER%"],
    "recreation": ["%REC%", "%GYM%", "%FITNESS%"],
    "parking": ["%PARKING%", "%GARAGE%"],
    "academic": ["%HALL%", "%SCIENCE%", "%ENGINEERING%"],
}


def _category_from_campus_locations(category: str, limit: int) -> List[CampusLocation]:
    """Query the curated campus_locations table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, category, address, building_number,
                   ST_Y(location_geo::geometry) as latitude,
                   ST_X(location_geo::geometry) as longitude,
                   description
            FROM campus_locations
            WHERE category = %s AND is_active = TRUE
            ORDER BY name
            LIMIT %s
        """, (category, limit))
        return [
            CampusLocation(
                id=r[0], name=r[1], category=r[2], address=r[3],
                building_number=r[4],
                coordinates=Coordinates(latitude=r[5], longitude=r[6]),
                description=r[7],
            )
            for r in cursor.fetchall()
        ]
    except Exception as e:
        logger.error(f"campus_locations query failed for category '{category}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def _category_from_campus_buildings(category: str, limit: int) -> List[CampusLocation]:
    """Fallback: search campus_buildings by name keywords."""
    patterns = _BUILDING_NAME_KEYWORDS.get(category, [])
    if not patterns:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Build OR conditions for each keyword pattern
        conditions = " OR ".join(["name ILIKE %s"] * len(patterns))
        query = f"""
            SELECT id, name, building_number,
                   ST_Y(ST_Centroid(geometry::geometry)) as latitude,
                   ST_X(ST_Centroid(geometry::geometry)) as longitude
            FROM campus_buildings
            WHERE {conditions}
            ORDER BY name
            LIMIT %s
        """
        cursor.execute(query, (*patterns, limit))
        locations = [
            CampusLocation(
                id=r[0], name=r[1], category=category,
                building_number=r[2],
                coordinates=Coordinates(latitude=r[3], longitude=r[4]),
                description="Campus building",
            )
            for r in cursor.fetchall()
        ]
        if locations:
            logger.info(f"Found {len(locations)} buildings for '{category}' via campus_buildings fallback")
        return locations
    except Exception as e:
        logger.error(f"campus_buildings fallback failed for category '{category}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_location_by_name(name: str) -> Optional[CampusLocation]:
    """
    Get a specific location by name with three-tier fallback:
      1. campus_locations table (exact match)
      2. campus_buildings table (ILIKE fuzzy match)
      3. Nominatim geocoding (online, biased to Mizzou campus)

    Args:
        name: Location name to search for

    Returns:
        CampusLocation if found, None otherwise
    """
    # --- Tier 1: campus_locations table ---
    result = _search_campus_locations(name)
    if result:
        return result

    # --- Tier 2: campus_buildings table (broader, ~376 buildings) ---
    result = _search_campus_buildings(name)
    if result:
        return result

    # --- Tier 3: Nominatim online geocoding ---
    return _geocode_as_location(name)


def _search_campus_locations(name: str) -> Optional[CampusLocation]:
    """Search the curated campus_locations table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, category, address, building_number,
                   ST_Y(location_geo::geometry) as latitude,
                   ST_X(location_geo::geometry) as longitude,
                   description
            FROM campus_locations
            WHERE LOWER(name) = LOWER(%s) AND is_active = TRUE
            LIMIT 1
        """, (name,))
        row = cursor.fetchone()
        if row:
            return CampusLocation(
                id=row[0], name=row[1], category=row[2],
                address=row[3], building_number=row[4],
                coordinates=Coordinates(latitude=row[5], longitude=row[6]),
                description=row[7],
            )
        return None
    except Exception as e:
        logger.error(f"campus_locations lookup failed for '{name}': {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def _search_campus_buildings(name: str) -> Optional[CampusLocation]:
    """Fallback: search the raw campus_buildings table with fuzzy matching."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, building_number,
                   ST_Y(ST_Centroid(geometry::geometry)) as latitude,
                   ST_X(ST_Centroid(geometry::geometry)) as longitude
            FROM campus_buildings
            WHERE LOWER(name) ILIKE LOWER(%s)
            LIMIT 1
        """, (f"%{name}%",))
        row = cursor.fetchone()
        if row:
            logger.info(f"Found '{name}' in campus_buildings (fallback tier 2)")
            return CampusLocation(
                id=row[0], name=row[1], category="misc",
                building_number=row[2],
                coordinates=Coordinates(latitude=row[3], longitude=row[4]),
                description="Campus building",
            )
        return None
    except Exception as e:
        logger.error(f"campus_buildings lookup failed for '{name}': {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def _geocode_as_location(name: str) -> Optional[CampusLocation]:
    """Fallback: use Nominatim geocoding (online, biased to Mizzou campus)."""
    try:
        coords = geocode_location(name)
        logger.info(f"Geocoded '{name}' online (fallback tier 3): {coords}")
        return CampusLocation(
            id=0,
            name=name.title(),
            category="misc",
            coordinates=coords,
            description="Found via online search",
        )
    except GeocodingError:
        logger.info(f"All lookup tiers failed for '{name}'")
        return None


def get_all_categories() -> List[str]:
    """
    Get list of all available location categories.
    
    Returns:
        List of category names
    """
    return [cat.value for cat in LocationCategory]


def get_locations_near(coordinates: Coordinates, radius_meters: int = 1000, 
                       category: Optional[str] = None, limit: int = 10) -> List[CampusLocation]:
    """
    Find locations near a given point.
    
    Args:
        coordinates: Center point for search
        radius_meters: Search radius in meters
        category: Optional category filter
        limit: Maximum results
        
    Returns:
        List of nearby CampusLocation objects, ordered by distance
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        base_query = """
            SELECT 
                id,
                name,
                category,
                address,
                building_number,
                ST_Y(location_geo::geometry) as latitude,
                ST_X(location_geo::geometry) as longitude,
                description,
                ST_Distance(
                    location_geo,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance
            FROM campus_locations
            WHERE is_active = TRUE
                AND ST_DWithin(
                    location_geo,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    %s
                )
        """
        
        params = [
            coordinates.longitude, coordinates.latitude,
            coordinates.longitude, coordinates.latitude,
            radius_meters
        ]
        
        if category:
            base_query += " AND category = %s"
            params.append(category)
        
        base_query += " ORDER BY distance LIMIT %s"
        params.append(limit)
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        locations = []
        for row in rows:
            locations.append(CampusLocation(
                id=row[0],
                name=row[1],
                category=row[2],
                address=row[3],
                building_number=row[4],
                coordinates=Coordinates(latitude=row[5], longitude=row[6]),
                description=row[7]
            ))
        
        return locations
        
    except Exception as e:
        logger.error(f"Error fetching nearby locations: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

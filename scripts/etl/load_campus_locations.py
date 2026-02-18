"""
Load and categorize campus locations from GeoJSON into the database.

This script reads the campus_buildings GeoJSON file and categorizes buildings
based on their names, then inserts them into the campus_locations table.
"""
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.app.db import get_db_connection
from src.backend.app.config import settings

# Category classification rules
CATEGORY_RULES = {
    "dorm": [
        "hall", "residence", "housing", "dormitory",
        # Specific Mizzou dorms
        "hatch", "mark twain", "college avenue", "gateway", "lathrop", 
        "laws", "johnston", "schurz", "gillett", "hudson", "jones", "defoe"
    ],
    "library": [
        "library", "libraries"
    ],
    "dining": [
        "dining", "cafeteria", "food", "plaza", "commons", "grill"
    ],
    "academic": [
        "building", "hall", "center", "laboratory", "lab", "classroom",
        "engineering", "science", "education", "arts", "school", "department"
    ],
    "recreation": [
        "rec", "recreation", "gym", "fitness", "stadium", "arena", "pool",
        "wellness", "field house", "athletic"
    ],
    "parking": [
        "parking", "garage", "lot"
    ]
}


def categorize_building(name: str) -> str:
    """
    Categorize a building based on its name.
    
    Args:
        name: Building name
        
    Returns:
        Category string (one of: dorm, library, dining, academic, recreation, parking, misc)
    """
    name_lower = name.lower()
    
    # Check each category's keywords
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in name_lower:
                # Special handling to avoid academic buildings being categorized as dorms
                if category == "dorm":
                    # Only categorize as dorm if it's actually residential
                    dorm_specific = ["residence", "housing", "dormitory", "hatch", "mark twain", 
                                   "college avenue", "gateway", "lathrop", "laws", "johnston"]
                    if any(kw in name_lower for kw in dorm_specific):
                        return "dorm"
                    # If just "hall" but not in dorm list, check if it's academic
                    if keyword == "hall" and any(acad in name_lower for acad in ["academic", "classroom", "lecture"]):
                        continue
                    # Known dorm halls
                    if keyword == "hall" and name_lower.endswith("hall"):
                        return "dorm"
                else:
                    return category
    
    return "misc"


def extract_buildings_from_geojson(geojson_path: str):
    """
    Extract building features from GeoJSON file.
    
    Args:
        geojson_path: Path to GeoJSON file
        
    Returns:
        List of building dictionaries with name, geometry, etc.
    """
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    buildings = []
    
    for feature in data.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry')
        
        # Get building name
        name = properties.get('name') or properties.get('NAME') or properties.get('bldg_name')
        if not name:
            continue
        
        # Get building number
        bldg_num = properties.get('bldg_num') or properties.get('building_number')
        
        # Calculate centroid for point location
        if geometry and geometry['type'] in ['Polygon', 'MultiPolygon']:
            coordinates = geometry['coordinates']
            
            # Simple centroid calculation
            if geometry['type'] == 'Polygon':
                coords_list = coordinates[0]  # exterior ring
            else:  # MultiPolygon
                coords_list = coordinates[0][0]  # first polygon, exterior ring
            
            # Calculate average lat/lon
            lons = [coord[0] for coord in coords_list]
            lats = [coord[1] for coord in coords_list]
            centroid_lon = sum(lons) / len(lons)
            centroid_lat = sum(lats) / len(lats)
            
            buildings.append({
                'name': name,
                'building_number': bldg_num,
                'category': categorize_building(name),
                'longitude': centroid_lon,
                'latitude': centroid_lat
            })
    
    return buildings


def load_campus_locations():
    """
    Main function to load campus locations into the database.
    """
    # Path to GeoJSON file
    data_dir = project_root / 'data' / 'campus_boundary'
    geojson_file = data_dir / 'campus_buildings_20260215.geojson'
    
    if not geojson_file.exists():
        print(f"Error: GeoJSON file not found at {geojson_file}")
        sys.exit(1)
    
    print(f"Loading buildings from {geojson_file}...")
    buildings = extract_buildings_from_geojson(str(geojson_file))
    
    print(f"Found {len(buildings)} buildings")
    
    # Categorize and count
    category_counts = {}
    for bldg in buildings:
        cat = bldg['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\nCategory breakdown:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        print("\nClearing existing campus_locations data...")
        cursor.execute("DELETE FROM campus_locations")
        
        # Insert buildings
        print("Inserting campus locations...")
        insert_query = """
            INSERT INTO campus_locations 
                (name, category, building_number, location_geo, address, is_active)
            VALUES 
                (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s, TRUE)
        """
        
        inserted = 0
        for bldg in buildings:
            try:
                cursor.execute(insert_query, (
                    bldg['name'],
                    bldg['category'],
                    bldg['building_number'],
                    bldg['longitude'],
                    bldg['latitude'],
                    f"Columbia, MO"  # Generic address
                ))
                inserted += 1
            except Exception as e:
                print(f"Warning: Failed to insert {bldg['name']}: {e}")
        
        conn.commit()
        print(f"\n✓ Successfully inserted {inserted} campus locations")
        
        # Show sample of each category
        print("\nSample locations by category:")
        for category in ['dorm', 'library', 'dining', 'academic', 'recreation']:
            cursor.execute("""
                SELECT name FROM campus_locations 
                WHERE category = %s 
                LIMIT 5
            """, (category,))
            locations = [row[0] for row in cursor.fetchall()]
            if locations:
                print(f"\n{category.upper()}:")
                for loc in locations:
                    print(f"  - {loc}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error loading data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_campus_locations()

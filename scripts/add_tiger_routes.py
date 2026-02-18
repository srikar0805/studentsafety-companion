"""
Add Tiger Line shuttle routes to the transit database with high precision.
Routes: Hearnes Loop (401), Trowbridge Loop (402), MU Reactor Loop (403),
        Campus Loop (405), MUHC Loop
Coordinates are matched from the shuttle_stops CSV file and manual mapping.
"""
import psycopg2
import csv
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Build coordinate lookup from CSV
def load_csv_coords():
    coords = {}
    with open('data/shuttle_data/shuttle_stops_20260215.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row['name'].strip().lower()
            lat, lng = float(row['lat']), float(row['lng'])
            coords[name] = (lat, lng)
    return coords

# Manual coordinate lookup for stop names that differ from CSV or need precise mapping
MANUAL_COORDS = {
    # General terms
    'wabash station': (38.9534, -92.3256),
    'mu student center': (38.9421, -92.3266),
    'hearnes center': (38.9324, -92.3295),
    'trowbridge': (38.9369, -92.3164),
    
    # Specific stop names from user list
    'rollins street at mu student center eastbound': (38.9421, -92.3266),
    'lake street & hitt street': (38.9392, -92.3253),
    'virginia avenue moi': (38.9365, -92.3254),
    'bus shelter on champions drive': (38.9325, -92.3295),
    'tiger avenue & hospital drive': (38.9384, -92.3307),
    'tiger avenue & kentucky boulevard': (38.9393, -92.3306),
    'rollins street at cornell hall': (38.9423, -92.3297),
    'bus shelter on rollins street at mu student center eastbound': (38.9421, -92.3266),
    
    'trowbridge bus shelter': (38.9369, -92.3164),
    'mu student center eastbound': (38.9421, -92.3266),
    'mu reactor lot': (38.9308, -92.3388),
    
    'mick deaver drive and champions drive': (38.9332, -92.3320),
    'conley avenue & tiger avenue': (38.9443, -92.3298),
    '6th street bus shelter at noyes hall': (38.9469, -92.3309),
    'turner avenue & fifth street': (38.9438, -92.3324),
    'laughlin memorial drive at reactor': (38.9308, -92.3388),
    'research park drive at reactor field': (38.9298, -92.3406),
    
    'hearnes bus shelter eastbound': (38.9324, -92.3295),
    'trowbridge bus shelter northbound': (38.9369, -92.3164),
    
    'hearnes center parking lot': (38.9324, -92.3295),
    'on champions drive, across from the hearnes shelter, eastbound': (38.9325, -92.3295),
    'hospital drive & monk drive': (38.9376, -92.3266),
}

TIGER_ROUTES = [
    {
        'number': 401,
        'name': 'Hearnes Loop (401)',
        'color': '#8B0000',
        'desc': 'Mon-Fri, 4:50am-8pm. Intervals: 10-20 min. Final departure 7:45pm.',
        'stops': [
            'Rollins Street at MU Student Center Eastbound',
            'Lake Street & Hitt Street',
            'Virginia Avenue MOI',
            'Bus Shelter on Champions Drive',
            'Tiger Avenue & Hospital Drive',
            'Tiger Avenue & Kentucky Boulevard',
            'Rollins Street at Cornell Hall',
            'Bus Shelter on Rollins Street at MU Student Center Eastbound'
        ]
    },
    {
        'number': 402,
        'name': 'Trowbridge Loop (402)',
        'color': '#F1B82D',
        'desc': 'Mon-Fri, 6am-8pm. Intervals: 10-20 min. Final departure 7:45pm.',
        'stops': [
            'Rollins Street at MU Student Center Eastbound',
            'Trowbridge Bus Shelter',
            'MU Student Center Eastbound'
        ]
    },
    {
        'number': 403,
        'name': 'MU Reactor Loop (403)',
        'color': '#4B0082',
        'desc': 'Mon-Fri, 6am-8pm. Intervals: 10-20 min. Final departure 7:50pm.',
        'stops': [
            'MU Reactor Lot',
            'Mick Deaver Drive and Champions Drive',
            'Tiger Avenue & Hospital Drive',
            'Tiger Avenue & Kentucky Boulevard',
            'Conley Avenue & Tiger Avenue',
            '6th Street Bus Shelter at Noyes Hall',
            'Turner Avenue & Fifth Street',
            'Laughlin Memorial Drive at Reactor',
            'Research Park Drive at Reactor Field'
        ]
    },
    {
        'number': 405,
        'name': 'Campus Loop (405)',
        'color': '#C41E3A',
        'desc': 'Sat & Sun, noon-8pm. 30-minute intervals. Final departure midnight.',
        'stops': [
            'Rollins Street at MU Student Center Eastbound',
            'Hearnes Bus Shelter Eastbound',
            'Trowbridge Bus Shelter Northbound',
            'MU Student Center Eastbound'
        ]
    },
    {
        'number': 406,
        'name': 'MUHC Loop',
        'color': '#2E8B57',
        'desc': 'Mon-Fri, 6:05-9:05am & 3:05-6:05pm. 10-minute intervals.',
        'stops': [
            'Hearnes Center Parking Lot',
            'Hospital Drive & Monk Drive',
            'On Champions Drive, across from the Hearnes Shelter, eastbound'
        ]
    },
]

def add_tiger_routes():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    csv_coords = load_csv_coords()
    
    print("🐯 Refining Tiger Line shuttle routes...\n")
    
    # First, clean existing Tiger Line routes/stops if they exist to avoid duplicates
    # Tiger Line routes are numbered 401, 402, 403, 405, or have specific names
    cur.execute("DELETE FROM transit_schedules WHERE route_id IN (SELECT id FROM transit_routes WHERE route_number IN (401, 402, 403, 405, 11, 406))")
    cur.execute("DELETE FROM transit_stops WHERE route_id IN (SELECT id FROM transit_routes WHERE route_number IN (401, 402, 403, 405, 11, 406))")
    cur.execute("DELETE FROM transit_routes WHERE route_number IN (401, 402, 403, 405, 11, 406)")
    conn.commit()
    
    for route in TIGER_ROUTES:
        # Insert route
        cur.execute("""
            INSERT INTO transit_routes (route_number, route_name, route_color, route_description, is_active)
            VALUES (%s, %s, %s, %s, TRUE) RETURNING id
        """, (route['number'], route['name'], route['color'], route['desc']))
        route_db_id = cur.fetchone()[0]
        
        print(f"🚌 {route['name']} (ID: {route_db_id})")
        
        # Insert stops
        for seq, stop_name in enumerate(route['stops'], 1):
            code = chr(64 + seq) if seq <= 26 else str(seq)
            
            # Look up coordinates
            key = stop_name.lower()
            lat, lng = None, None
            
            # Check manual coords first
            if key in MANUAL_COORDS:
                lat, lng = MANUAL_COORDS[key]
            # Then check CSV
            elif key in csv_coords:
                lat, lng = csv_coords[key]
            else:
                # Fuzzy match in CSV
                for csv_name, (clat, clng) in csv_coords.items():
                    if key in csv_name or csv_name in key:
                        lat, lng = clat, clng
                        break
            
            if lat and lng:
                cur.execute("""
                    INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence, location_geo, is_timepoint)
                    VALUES (%s, %s, %s, %s, ST_GeogFromText('POINT(%s %s)'), FALSE)
                """, (route_db_id, code, stop_name, seq, lng, lat))
                print(f"   ✓ {code}: {stop_name} ({lat:.4f}, {lng:.4f})")
            else:
                cur.execute("""
                    INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence, is_timepoint)
                    VALUES (%s, %s, %s, %s, FALSE)
                """, (route_db_id, code, stop_name, seq))
                print(f"   ⚠ {code}: {stop_name} (no coordinates found)")
    
    conn.commit()
    print(f"\n✅ All Tiger Line routes updated successfully!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_tiger_routes()

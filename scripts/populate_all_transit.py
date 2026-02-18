"""
Populate ALL transit stops from the CSV file.
The CSV groups stops by route, separated by "Wabash Station" entries.
We use the full set of unique stops per route with GPS coordinates.
"""
import psycopg2
import csv
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Route definitions matching the CSV order
# CSV analysis shows routes are separated by "Wabash Station" entries
ROUTE_DEFS = {
    1: {'name': 'Black - MU/Providence South', 'color': '#333333', 'desc': 'Campus and south Columbia via Providence'},
    2: {'name': 'Red - West Broadway', 'color': '#DC143C', 'desc': 'Downtown and west Columbia via Broadway'},
    3: {'name': 'Gold - West Worley', 'color': '#FFD700', 'desc': 'Central and west Columbia via Worley'},
    4: {'name': 'Orange - Rangeline North', 'color': '#FF8C00', 'desc': 'North Columbia via Rangeline'},
    5: {'name': 'Blue - Paris/Clark/Ballenger', 'color': '#4169E1', 'desc': 'North and east Columbia via Clark Lane'},
    6: {'name': 'Green - East Broadway/Keene', 'color': '#228B22', 'desc': 'East Columbia via Broadway and Keene'},
}

# Keywords to identify which CSV group belongs to which route
ROUTE_IDENTIFIERS = {
    1: ['green meadow', 'south providence', 'nifong', 'carter lane'],
    2: ['west broadway', 'walmart', 'briarwood', 'clinkscales', 'park de ville', 'fairview'],
    3: ['oak towers', 'west worley', 'bernadette', 'food bank', 'sexton'],
    4: ['rangeline', 'ashley street', 'brown school', 'derby ridge', 'smiley'],
    5: ['ballenger', 'clark lane', 'whitegate', 'hanover', 'rice road', 'mckee'],
    6: ['boone hospital', 'broadway village', 'keene', 'conley road', 'trimble'],
}

def identify_route(stop_names_lower):
    """Identify which route a group of stops belongs to."""
    scores = {}
    for route_num, keywords in ROUTE_IDENTIFIERS.items():
        score = sum(1 for kw in keywords if any(kw in name for name in stop_names_lower))
        scores[route_num] = score
    
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return 0

def populate():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Clean existing data
    print("🗑️  Cleaning existing transit data...")
    cur.execute("DELETE FROM transit_schedules")
    cur.execute("DELETE FROM transit_stops")
    cur.execute("DELETE FROM transit_routes")
    conn.commit()
    
    # Read CSV
    all_stops = []
    with open('data/shuttle_data/shuttle_stops_20260215.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_stops.append({
                'stop_id': row['stop_id'],
                'name': row['name'].strip(),
                'lat': float(row['lat']),
                'lng': float(row['lng'])
            })
    
    print(f"📄 Read {len(all_stops)} stops from CSV")
    
    # Split into route groups by "Wabash Station"
    groups = []
    current = []
    for stop in all_stops:
        current.append(stop)
        if stop['name'] == 'Wabash Station' and len(current) > 1:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    
    print(f"📊 Found {len(groups)} route groups")
    
    # Insert routes
    route_db_ids = {}
    for route_num, info in ROUTE_DEFS.items():
        cur.execute("""
            INSERT INTO transit_routes (route_number, route_name, route_color, route_description, is_active)
            VALUES (%s, %s, %s, %s, TRUE) RETURNING id
        """, (route_num, info['name'], info['color'], info['desc']))
        route_db_ids[route_num] = cur.fetchone()[0]
    conn.commit()
    print(f"✅ Inserted {len(route_db_ids)} routes")
    
    # Assign groups to routes and insert stops
    used_routes = set()
    
    for group in groups:
        names_lower = [s['name'].lower() for s in group]
        route_num = identify_route(names_lower)
        
        if route_num == 0 or route_num in used_routes:
            # Try harder - check remaining routes
            for rn in ROUTE_DEFS:
                if rn not in used_routes:
                    route_num = rn
                    break
            if route_num in used_routes:
                print(f"  ⚠️  Skipping extra group ({len(group)} stops)")
                continue
        
        used_routes.add(route_num)
        route_db_id = route_db_ids[route_num]
        route_name = ROUTE_DEFS[route_num]['name']
        
        # Deduplicate stops by name within route
        seen = set()
        unique_stops = []
        for stop in group:
            if stop['name'] not in seen:
                seen.add(stop['name'])
                unique_stops.append(stop)
        
        # Insert stops
        for seq, stop in enumerate(unique_stops, 1):
            code = chr(64 + seq) if seq <= 26 else f"A{chr(64 + seq - 26)}"
            cur.execute("""
                INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence, location_geo, is_timepoint)
                VALUES (%s, %s, %s, %s, ST_GeogFromText('POINT(%s %s)'), %s)
            """, (route_db_id, code, stop['name'], seq, stop['lng'], stop['lat'],
                  stop['name'] == 'Wabash Station'))
        
        print(f"  🚌 Route {route_num} ({route_name}): {len(unique_stops)} stops")
    
    conn.commit()
    
    # Summary
    cur.execute("SELECT COUNT(*) FROM transit_stops WHERE location_geo IS NOT NULL")
    total = cur.fetchone()[0]
    
    cur.execute("""
        SELECT r.route_name, r.route_color, COUNT(s.id) 
        FROM transit_routes r LEFT JOIN transit_stops s ON r.id = s.route_id 
        GROUP BY r.route_name, r.route_color, r.route_number ORDER BY r.route_number
    """)
    
    print(f"\n{'='*50}")
    print(f"✅ COMPLETE: {total} stops with GPS coordinates")
    print(f"\nPer-route breakdown:")
    for name, color, count in cur.fetchall():
        print(f"  {color} {name}: {count} stops")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    populate()

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check routes
cur.execute("SELECT id, route_number, route_name FROM transit_routes")
routes = cur.fetchall()
print(f"Routes in database: {len(routes)}")
for r in routes:
    print(f"  {r}")

# Check stops
cur.execute("SELECT COUNT(*) FROM transit_stops")
stop_count = cur.fetchone()[0]
print(f"\nStops in database: {stop_count}")

# If no stops, let's insert them manually for Route 1
if stop_count == 0:
    print("\nInserting stops for Black Route...")
    
    # Get route 1 ID
    cur.execute("SELECT id FROM transit_routes WHERE route_number = 1")
    route_1_id = cur.fetchone()[0]
    
    stops = [
        ('A', 'Wabash Station', 1, 38.95344543457031, -92.32564544677734),
        ('B', 'Tiger Ave & Conley Ave', 2, 38.94431686401367, -92.3298110961914),
        ('C', 'Tiger Ave at Residence Halls', 3, 38.93836212158203, -92.33079528808594),
        ('D', 'Green Meadow Rd & Carter Ln', 4, 38.917171478271484, -92.33279418945312),
        ('E', 'South Providence Medical Plaza', 5, 38.90037155151367, -92.33193969726562),
        ('F', 'Green Meadow Rd & Carter Ln', 6, 38.917171478271484, -92.33279418945312),
        ('G', 'Tiger Ave & Hospital Dr', 7, 38.9383544921875, -92.33065032958984),
        ('H', 'Tiger Ave & Conley Ave', 8, 38.94431686401367, -92.3298110961914),
        ('I', 'Arrive Wabash Station', 9, 38.95344543457031, -92.32564544677734),
    ]
    
    for code, name, seq, lat, lng in stops:
        cur.execute("""
            INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence, location_geo)
            VALUES (%s, %s, %s, %s, ST_GeogFromText('POINT(%s %s)'))
        """, (route_1_id, code, name, seq, lng, lat))
        print(f"  ✓ Added stop {code}: {name}")
    
    conn.commit()
    print("\n✅ Stops inserted!")

# Verify
cur.execute("""
    SELECT stop_code, stop_name, ST_Y(location_geo::geometry) as lat, ST_X(location_geo::geometry) as lng
    FROM transit_stops 
    WHERE location_geo IS NOT NULL
    ORDER BY stop_code
""")

print("\nAll stops with coordinates:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} - ({row[2]:.6f}, {row[3]:.6f})")

cur.close()
conn.close()

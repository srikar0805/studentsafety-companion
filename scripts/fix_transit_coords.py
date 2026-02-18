import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Check what stops we have and update with coordinates
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get all stops
cur.execute("""
    SELECT id, route_id, stop_name 
    FROM transit_stops 
    WHERE route_id = 1
    ORDER BY stop_sequence
""")

stops = cur.fetchall()
print("Transit stops from database (Route 1 - Black):")
for stop_id, route_id, name in stops:
    print(f"  {name}")

# Use simplified matching - direct coordinate assignment by stop code/sequence
coords_by_code = {
    'A': (38.95344543457031, -92.32564544677734),  # Wabash Station - START
    'B': (38.94431686401367, -92.3298110961914),  # Tiger Ave & Conley Ave
    'C': (38.93836212158203, -92.33079528808594),  # Tiger Ave at Residence Halls  
    'D': (38.917171478271484, -92.33279418945312),  # Green Meadow Rd & Carter Ln (North)
    'E': (38.90037155151367, -92.33193969726562),  # South Providence Medical Plaza
    'F': (38.917171478271484, -92.33279418945312),  # Green Meadow Rd & Carter Ln (South - same as D)
    'G': (38.9383544921875, -92.33065032958984),  # Tiger Ave & Hospital Dr
    'H': (38.94431686401367, -92.3298110961914),  # Tiger Ave & Conley Ave (same as B)
    'I': (38.95344543457031, -92.32564544677734),  # Arrive Wabash Station (same as A)
}

print("\nUpdating coordinates...")
cur.execute("SELECT id, stop_code FROM transit_stops WHERE route_id = 1")
stops = cur.fetchall()

updated = 0
for stop_id, stop_code in stops:
    if stop_code in coords_by_code:
        lat, lng = coords_by_code[stop_code]
        cur.execute("""
            UPDATE transit_stops
            SET location_geo = ST_GeogFromText('POINT(%s %s)')
            WHERE id = %s
        """, (lng, lat, stop_id))
        print(f"  ✓ Stop {stop_code}: ({lat}, {lng})")
        updated += 1

conn.commit()
print(f"\n✅ Updated {updated} stops with coordinates!")

# Verify
cur.execute("""
    SELECT stop_code, stop_name, ST_Y(location_geo::geometry) as lat, ST_X(location_geo::geometry) as lng
    FROM transit_stops 
    WHERE route_id = 1 AND location_geo IS NOT NULL
    ORDER BY stop_code
""")

print("\nVerifying coordinates:")
for row in cur.fetchall():
    print(f" ✓ {row[0]}: {row[1]} - ({row[2]:.6f}, {row[3]:.6f})")

cur.close()
conn.close()

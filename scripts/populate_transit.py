import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("🚌 Populating CoMo Transit data...")

# Insert routes
routes = [
    (1, 'Black Route', '#000000', 'Wabash - Green Meadows - Soco'),
    (2, 'Red Route', '#FF0000', 'Wabash - West Blvd - Walmart'),
    (3, 'Gold Route', '#FFD700', 'Wabash - Oakland - Mall'),
    (4, 'Orange Route', '#FFA500', 'Wabash - North Providence - Rangeline'),
    (5, 'Blue Route', '#0000FF', 'Wabash - Clark Ln'),
    (6, 'Green Route', '#00FF00', 'Wabash - Broadway - Boone Hospital'),
]

print("\nInserting routes...")
for num, name, color, desc in routes:
    cur.execute("""
        INSERT INTO transit_routes (route_number, route_name, route_color, route_description, is_active)
        VALUES (%s, %s, %s, %s, TRUE)
        ON CONFLICT DO NOTHING
    """, (num, name, color, desc))
    print(f"  ✓ Route {num}: {name}")

conn.commit()

# Get route IDs
cur.execute("SELECT id, route_number FROM transit_routes ORDER BY route_number")
route_map = {num: id for id, num in cur.fetchall()}

# Insert stops for Black Route (route 1)
print("\nInserting Black Route stops...")
stops_route_1 = [
    ('A', 'Wabash Station', 1, 38.95344543457031, -92.32564544677734, True),
    ('B', 'Tiger Ave & Conley Ave', 2, 38.94431686401367, -92.3298110961914, False),
    ('C', 'Tiger Ave at Residence Halls', 3, 38.93836212158203, -92.33079528808594, False),
    ('D', 'Green Meadow Rd & Carter Ln', 4, 38.917171478271484, -92.33279418945312, False),
    ('E', 'South Providence Medical Plaza', 5, 38.90037155151367, -92.33193969726562, True),
    ('F', 'Green Meadow Rd & Carter Ln', 6, 38.917171478271484, -92.33279418945312, False),
    ('G', 'Tiger Ave & Hospital Dr', 7, 38.9383544921875, -92.33065032958984, False),
    ('H', 'Tiger Ave & Conley Ave', 8, 38.94431686401367, -92.3298110961914, False),
    ('I', 'Arrive Wabash Station', 9, 38.95344543457031, -92.32564544677734, True),
]

for code, name, seq, lat, lng, is_timepoint in stops_route_1:
    cur.execute("""
        INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence, location_geo, is_timepoint)
        VALUES (%s, %s, %s, %s, ST_GeogFromText('POINT(%s %s)'), %s)
    """, (route_map[1], code, name, seq, lng, lat, is_timepoint))
    print(f"  ✓ Stop {code}: {name}")

# Insert stops for Red Route (route 2)
print("\nInserting Red Route stops...")
stops_route_2 = [
    ('A', 'Wabash Station', 1, 38.95344543457031, -92.32564544677734, True),
    ('B', 'Columbia Library', 2, 38.951568603515625, -92.34083557128906, False),
    ('C', 'Broadway & West Blvd', 3, 38.95202636718750, -92.35234069824219, True),
    ('D', 'Crossroads shopping center', 4, 38.95412063598633, -92.37246704101562, False),
    ('E', 'Walmart West', 5, 38.95450210571289, -92.37955474853516, True),
    ('F', 'Crossroads shopping center', 6, 38.95412063598633, -92.37246704101562, False),
    ('G', 'Broadway & West Blvd', 7, 38.95202636718750, -92.35234069824219, True),
    ('H', 'Columbia Library', 8, 38.951568603515625, -92.34083557128906, False),
    ('I', 'Arrive Wabash Station', 9, 38.95344543457031, -92.32564544677734, True),
]

for code, name, seq, lat, lng, is_timepoint in stops_route_2:
    cur.execute("""
        INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence, location_geo, is_timepoint)
        VALUES (%s, %s, %s, %s, ST_GeogFromText('POINT(%s %s)'), %s)
    """, (route_map[2], code, name, seq, lng, lat, is_timepoint))
    print(f"  ✓ Stop {code}: {name}")

conn.commit()

# Verify
cur.execute("""
    SELECT COUNT(*) FROM transit_routes
""")
route_count = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*) FROM transit_stops WHERE location_geo IS NOT NULL
""")
stop_count = cur.fetchone()[0]

print(f"\n✅ Success!")
print(f"   - {route_count} routes inserted")
print(f"   - {stop_count} stops with coordinates")

cur.close()
conn.close()

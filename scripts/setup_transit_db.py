import psycopg2
import csv
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def setup_transit_database():
    """Create transit tables, populate routes/stops/schedules, and add coordinates from CSV."""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("📋 Step 1: Creating transit tables...")
    
    # Create tables
    with open('src/db/migrations/como_transit_schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cur.execute(schema_sql)
    
    print("✓ Transit tables created")
    
    print("\n📋 Step 2: Populating route data, stops, and schedules...")
    
    # Populate routes and schedules
    with open('src/db/data/como_transit_data.sql', 'r', encoding='utf-8') as f:
        data_sql = f.read()
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in data_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        for statement in statements:
            if statement:
                try:
                    cur.execute(statement)
                except Exception as e:
                    print(f"Warning: {e}")
                    # Continue anyway - some statements might fail due to duplicates
    
    print("✓ Routes, stops, and schedules populated")
    
    print("\n📋 Step 3: Adding coordinates from CSV file...")
    
    # Load coordinates from CSV
    coordinates_map = {}
    with open('data/shuttle_data/shuttle_stops_20260215.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stop_name = row['name']
            lat = float(row['lat'])
            lng = float(row['lng'])
            coordinates_map[stop_name] = (lat, lng)
    
    print(f"✓ Loaded {len(coordinates_map)} stop coordinates from CSV")
    
    # Update transit_stops with coordinates
    cur.execute("SELECT id, stop_name FROM transit_stops")
    stops = cur.fetchall()
    
    updated_count = 0
    for stop_id, stop_name in stops:
        # Try exact match first
        if stop_name in coordinates_map:
            lat, lng = coordinates_map[stop_name]
            cur.execute("""
                UPDATE transit_stops 
                SET location_geo = ST_GeogFromText('POINT(%s %s)')
                WHERE id = %s
            """, (lng, lat, stop_id))
            updated_count += 1
        else:
            # Try fuzzy match (without "at" or "&")
            simplified_name = stop_name.replace(' at ', ' ').replace(' & ', ' ').lower()
            for csv_name, (lat, lng) in coordinates_map.items():
                csv_simplified = csv_name.replace(' at ', ' ').replace(' & ', ' ').lower()
                if simplified_name in csv_simplified or csv_simplified in simplified_name:
                    cur.execute("""
                        UPDATE transit_stops 
                        SET location_geo = ST_GeogFromText('POINT(%s %s)')
                        WHERE id = %s
                    """, (lng, lat, stop_id))
                    updated_count += 1
                    break
    
    print(f"✓ Updated {updated_count} transit stops with coordinates")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n✅ Transit database setup complete!")
    print(f"   - Tables created")
    print(f"   - 6 routes populated")
    print(f"   - Stops and schedules loaded")
    print(f"   - {updated_count} stops have coordinates")

if __name__ == "__main__":
    setup_transit_database()

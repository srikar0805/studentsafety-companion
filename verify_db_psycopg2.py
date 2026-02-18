import psycopg2
import os
import sys

# Get DB URL from env or use the one provided by user
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    tables = [
        "crime_incidents", 
        "cpd_incidents", 
        "safety_assets", 
        "shuttle_stops", 
        "campus_buildings", 
        "police_calls"
    ]
    
    print(f"Checking database: {DB_URL.split('@')[1]}") # Print host only for safety
    print("-" * 30)
    
    found_data = False
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"{table}: {count}")
            if count > 0:
                found_data = True
        except psycopg2.errors.UndefinedTable:
            conn.rollback()
            print(f"{table}: Table not found (Scheme not initialized?)")
        except Exception as e:
            conn.rollback()
            print(f"{table}: Error {e}")
            
    conn.close()
    
    if not found_data:
        print("\nCONCLUSION: Database is EMPTY or tables are missing.")
    else:
        print("\nCONCLUSION: Database contains data.")

except Exception as e:
    print(f"Connection failed: {e}")

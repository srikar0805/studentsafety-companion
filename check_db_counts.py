
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            tables = ["crime_incidents", "cpd_incidents", "safety_assets", "shuttle_stops", "campus_buildings", "police_calls"]
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"{table}: {count}")
                except Exception as e:
                    print(f"Error querying {table}: {e}")
                    conn.rollback()

except Exception as e:
    print(f"Connection failed: {e}")

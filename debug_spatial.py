
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

# Student Center (approx)
lon = -92.326637
lat = 38.942108

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # Check safety assets group by type
            sql = """
                SELECT asset_type, COUNT(*) 
                FROM safety_assets 
                WHERE ST_DWithin(
                    location_geo, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326), 
                    500
                )
                GROUP BY asset_type
            """
            cur.execute(sql, (lon, lat))
            print(f"Safety Assets within 500m: {cur.fetchall()}")

            # Check incidents
            sql = """
                SELECT COUNT(*) 
                FROM crime_incidents 
                WHERE ST_DWithin(
                    location_geo, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326), 
                    500
                )
            """
            cur.execute(sql, (lon, lat))
            print(f"MUPD Incidents within 500m: {cur.fetchone()[0]}")

            # Check CPD incidents
            sql = """
                SELECT COUNT(*) 
                FROM cpd_incidents 
                WHERE ST_DWithin(
                    location_geo, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326), 
                    500
                )
                AND report_date >= NOW() - INTERVAL '30 days'
            """
            cur.execute(sql, (lon, lat))
            print(f"CPD Incidents within 500m (30 days): {cur.fetchone()[0]}")

except Exception as e:
    print(f"Error: {e}")


import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

# From previous logs
wkt = "LINESTRING(-92.326717 38.942182, -92.328376 38.942204, -92.329993 38.942359, -92.329893 38.944442, -92.330979 38.944562, -92.33087 38.948558, -92.327615 38.948509, -92.327577 38.945908, -92.327814 38.945815, -92.327854 38.945423, -92.328205 38.945432)"
radius_m = 100

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            sql = """
                SELECT COUNT(*)
                FROM safety_assets 
                WHERE ST_DWithin(
                    location_geo, 
                    ST_GeogFromText(%s), 
                    %s
                )
                AND asset_type ILIKE 'Emergency Phone%'
            """
            cur.execute(sql, (wkt, radius_m))
            print(f"Safety Assets within {radius_m}m of route: {cur.fetchone()[0]}")
            
            # Try larger radius
            cur.execute(sql, (wkt, 500))
            print(f"Safety Assets within 500m of route: {cur.fetchone()[0]}")

except Exception as e:
    print(f"Error: {e}")

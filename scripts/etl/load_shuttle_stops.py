
import os
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_CONN = os.getenv("DATABASE_URL")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data"))
SHUTTLE_DIR = os.path.join(DATA_ROOT, "shuttle_data")

def get_engine():
    return create_engine(DB_CONN)

def load_shuttle_stops(engine):
    print("\n--- Loading Shuttle Stops ---")
    files = [f for f in os.listdir(SHUTTLE_DIR) if f.startswith("shuttle_stops")]
    if not files:
        print("No shuttle stops file found.")
        return
    
    file_path = os.path.join(SHUTTLE_DIR, sorted(files)[-1])
    print(f"Reading {file_path}")
    df = pd.read_csv(file_path)
    
    if df.empty:
        print("File is empty.")
        return

    print(f"Found {len(df)} stops.")

    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                sid = row['stop_id']
                name = row['name']
                lat = row['lat']
                lng = row['lng']
                
                wkt = f"POINT({lng} {lat})"
                
                sql = text("""
                    INSERT INTO shuttle_stops (stop_id, stop_name, location_geo)
                    VALUES (:sid, :name, ST_SetSRID(ST_GeomFromText(:wkt), 4326))
                    ON CONFLICT (stop_id) DO UPDATE 
                    SET stop_name = EXCLUDED.stop_name,
                        location_geo = EXCLUDED.location_geo;
                """)
                
                conn.execute(sql, {"sid": sid, "name": name, "wkt": wkt})
                conn.commit()
            except Exception as e:
                print(f"Error stop {row.get('stop_id')}: {e}")
                
    print("Shuttle Stops Loaded.")

if __name__ == "__main__":
    engine = get_engine()
    load_shuttle_stops(engine)

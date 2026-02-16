import os
import pandas as pd
import geopandas as gpd
import json
import psycopg2
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry, WKTElement
import datetime
import polyline
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DB_CONN = os.getenv("DATABASE_URL")

# Directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data"))

# Paths
MUPD_DIR = os.path.join(DATA_ROOT, "crime_logs")
CPD_DIR = os.path.join(DATA_ROOT, "crime_logs")
SHUTTLE_DIR = os.path.join(DATA_ROOT, "shuttle_data")
CAMPUS_DIR = os.path.join(DATA_ROOT, "campus_boundary")

def get_engine():
    return create_engine(DB_CONN)

def load_mupd_crime_logs(engine):
    print("\n--- Loading MUPD Crime Logs ---")
    files = [f for f in os.listdir(MUPD_DIR) if f.startswith("mupd_crime_log")]
    if not files: return
    
    file_path = os.path.join(MUPD_DIR, sorted(files)[-1])
    df = pd.read_csv(file_path)
    if df.empty: return

    def parse_dt(x):
        try: return pd.to_datetime(x)
        except: return None
            
    df['date_reported'] = df['Date/Time Reported'].apply(parse_dt)
    df['date_occurred'] = df['date_reported'] # Fallback
    
    # DB Columns: case_number, date_reported, date_occurred, location_name, incident_type, disposition
    # CSV Columns: Case Number, Date/Time Reported, Location of Occurence, Incident Type, Disposition
    
    insert_data = df.rename(columns={
        'Case Number': 'case_number',
        'Location of Occurence': 'location_name',
        'Incident Type': 'incident_type',
        'Disposition': 'disposition'
    })[['case_number', 'date_reported', 'date_occurred', 'location_name', 'incident_type', 'disposition']]
    
    try:
        insert_data.to_sql('crime_incidents_temp', engine, if_exists='replace', index=False)
        
        with engine.connect() as conn:
            # Fix column names in INSERT
            conn.execute(text("""
                INSERT INTO crime_incidents (case_number, date_reported, date_occurred, location_name, incident_type, disposition)
                SELECT case_number, date_reported, date_occurred, location_name, incident_type, disposition
                FROM crime_incidents_temp
                ON CONFLICT (case_number) DO NOTHING;
            """))
            conn.commit() 
        print("MUPD Crime Logs Loaded.")
    except Exception as e:
        print(f"Error loading MUPD: {e}")

def load_cpd_crime_data(engine):
    print("\n--- Loading CPD Crime Logs ---")
    files = [f for f in os.listdir(CPD_DIR) if f.startswith("cpd_crime_data")]
    if not files: return
    
    df = pd.read_csv(os.path.join(CPD_DIR, sorted(files)[-1]))
    if df.empty: return

    # Clean
    df['report_date'] = pd.to_datetime(df['report_date'])
    
    print(f"CPD: Found {len(df)} rows.")
    with engine.connect() as conn:
        count = 0
        for _, row in df.iterrows():
            try:
                # Create Point Geometry
                if pd.notnull(row['x']) and pd.notnull(row['y']):
                    count += 1
                    # ArcGIS usually x=lon, y=lat
                    wkt = f"POINT({row['x']} {row['y']})" 
                    
                    sql = text("""
                        INSERT INTO cpd_incidents (offense_id, report_date, nibrs_description, full_address, location_geo)
                        VALUES (:oid, :rdate, :desc, :addr, ST_SetSRID(ST_GeomFromText(:wkt), 4326))
                        ON CONFLICT (offense_id) DO NOTHING;
                    """)
                    
                    conn.execute(sql, {
                        "oid": str(row['offense_id']),
                        "rdate": row['report_date'],
                        "desc": row['nibrs_description'],
                        "addr": row['full_address'],
                        "wkt": wkt
                    })
                    conn.commit()
            except Exception as e:
                print(f"Error cpd row: {e}") 
                pass
    print("CPD Crime Data Loaded.")

def load_shuttle_routes(engine):
    print("\n--- Loading Shuttle Routes ---")
    files = [f for f in os.listdir(SHUTTLE_DIR) if f.startswith("shuttle_routes")]
    if not files: return
    
    df = pd.read_csv(os.path.join(SHUTTLE_DIR, sorted(files)[-1]))
    
    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                # Decode polyline
                encoded = row.get('encoded_polyline')
                if not encoded: continue
                
                points = polyline.decode(encoded) # [(lat, lon), ...]
                if not points: continue
                
                # WKT needs (lon, lat)
                coords = ", ".join([f"{lon} {lat}" for lat, lon in points])
                wkt = f"LINESTRING({coords})"
                
                rid = row.get('route_id')
                # If rid is missing/NaN, use hash
                if pd.isna(rid):
                    rid = abs(hash(row.get('name', 'unknown'))) % 100000
                
                name = row.get('name')
                
                sql = text("""
                    INSERT INTO shuttle_routes (route_id, route_name, geometry)
                    VALUES (:rid, :name, ST_GeomFromText(:wkt, 4326))
                    ON CONFLICT (route_id) DO UPDATE SET geometry = EXCLUDED.geometry;
                """)
                
                conn.execute(sql, {"rid": rid, "name": name, "wkt": wkt})
                conn.commit()
            except Exception as e:
                print(f"Error route {row.get('name')}: {e}")
                
    print("Shuttle Routes Loaded.")

def load_campus_geojson(engine, filename_pattern, table_name, feature_type):
    print(f"\n--- Loading {table_name} ---")
    files = [f for f in os.listdir(CAMPUS_DIR) if f.startswith(filename_pattern) and f.endswith(".geojson")]
    if not files: return

    path = os.path.join(CAMPUS_DIR, sorted(files)[-1])
    with open(path) as f:
        data = json.load(f)
        
    with engine.connect() as conn:
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            if not geom: continue
            
            geom_json = json.dumps(geom)
            name = props.get('NAME') or props.get('name') or "Unknown"
            
            # Use ST_Multi to cast to MULTIPOLYGON
            sql = text(f"""
                INSERT INTO {table_name} (name, geometry)
                VALUES (:name, ST_Multi(ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))))
            """)
            
            try:
                with conn.begin_nested():
                    conn.execute(sql, {"name": name, "geom": geom_json})
            except Exception as e:
                print(f"Skipping {name}: {e}")
        conn.commit() # Commit the transaction!
                
    print(f"{table_name} Loaded.")

def load_safety_assets(engine):
    print("\n--- Loading Safety Assets ---")
    # Phones
    files_phones = [f for f in os.listdir(CAMPUS_DIR) if "emergency_phones" in f]
    if files_phones:
        path = os.path.join(CAMPUS_DIR, sorted(files_phones)[-1])
        _load_asset_file(engine, path, 'Emergency Phone')
        
    # Entrances
    files_entrances = [f for f in os.listdir(CAMPUS_DIR) if "accessible_entrances" in f]
    if files_entrances:
        path = os.path.join(CAMPUS_DIR, sorted(files_entrances)[-1])
        _load_asset_file(engine, path, 'Accessible Entrance')

def _load_asset_file(engine, path, asset_type):
    with open(path) as f:
        data = json.load(f)
        
    with engine.connect() as conn:
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            if not geom: continue
            
            oid = props.get('OBJECTID')
            desc = props.get('NOTES') or props.get('LOC')
            geom_json = json.dumps(geom)
            
            sql = text("""
                INSERT INTO safety_assets (asset_id, asset_type, description, location_geo)
                VALUES (:oid, :type, :desc, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))
                ON CONFLICT DO NOTHING; -- Schema doesn't have unique constraint on oid yet, but good practice
            """)
            
            try:
                conn.execute(sql, {"oid": oid, "type": asset_type, "desc": desc, "geom": geom_json})
                conn.commit()
            except Exception as e:
                print(f"Error asset {oid}: {e}")
    print(f"Loaded {asset_type}")


if __name__ == "__main__":
    engine = get_engine()
    load_mupd_crime_logs(engine)
    load_cpd_crime_data(engine)
    load_shuttle_routes(engine)
    load_campus_geojson(engine, "campus_boundary", "campus_boundary", "Polygon")
    load_campus_geojson(engine, "campus_buildings", "campus_buildings", "Polygon")
    load_safety_assets(engine)
    print("\nData Load Complete.")

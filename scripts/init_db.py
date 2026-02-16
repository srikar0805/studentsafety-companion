
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Configuration
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASS = "" # Assuming no password for local dev
DB_NAME = "studentsafety"

def init_db():
    # 1. Connect to default 'postgres' db to create the new db
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if db exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cur.execute(f"CREATE DATABASE {DB_NAME}")
        else:
            print(f"Database '{DB_NAME}' already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating DB: {e}")
        return

    # 2. Connect to the new DB to enable PostGIS and Apply Schema
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("Enabling PostGIS extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # Read schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "../src/db/schema.sql")
        print(f"Applying schema from {schema_path}...")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
            cur.execute(schema_sql)
            
        print("Schema applied successfully.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error applying schema: {e}")

if __name__ == "__main__":
    init_db()

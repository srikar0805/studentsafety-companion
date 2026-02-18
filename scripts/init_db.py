import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
DB_URL = os.getenv("DATABASE_URL")

def init_db():
    if not DB_URL:
        print("Error: DATABASE_URL not found in environment.")
        return

    try:
        # Use simple connection for initial setup if needed, 
        # but Supabase usually has a single DB name (often 'postgres')
        print(f"Connecting to database to apply schema...")
        conn = psycopg2.connect(DB_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("Enabling PostGIS extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # Read schema.sql
        # Path relative to project root since this is run as 'python scripts/init_db.py'
        schema_path = os.path.join(os.path.dirname(__file__), "../src/db/schema.sql")
        print(f"Applying schema from {schema_path}...")
        
        with open(schema_path, "r") as f:
            schema_sql = f.read()
            # Split schema by ';' to execute statements (if needed) or execute all
            # psycopg2 can execute multiple statements separated by ; in one go
            cur.execute(schema_sql)
            
        print("Schema applied successfully.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error applying schema: {e}")

if __name__ == "__main__":
    init_db()

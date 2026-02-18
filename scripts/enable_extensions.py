import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Enabling postgis...")
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        print("postgis enabled.")
    except Exception as e:
        print(f"Failed to enable postgis: {e}")
        
    print("Enabling vector...")
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("vector enabled.")
    except Exception as e:
        print(f"Failed to enable vector: {e}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed to connect: {e}")


import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tablename, indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename IN ('crime_incidents', 'cpd_incidents');
            """)
            for row in cur.fetchall():
                print(row)
except Exception as e:
    print(f"Error: {e}")


import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT MIN(date_occurred), MAX(date_occurred) FROM crime_incidents")
            print(f"MUPD: {cur.fetchone()}")
            
            cur.execute("SELECT MIN(report_date), MAX(report_date) FROM cpd_incidents")
            print(f"CPD: {cur.fetchone()}")
except Exception as e:
    print(f"Error: {e}")

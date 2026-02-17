import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        for table in ["crime_incidents", "police_calls", "cpd_incidents"]:
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position",
                (table,)
            )
            cols = [r[0] for r in cur.fetchall()]
            print(f"\n=== {table} ===")
            for c in cols:
                print(f"  {c}")

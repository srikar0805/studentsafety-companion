import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONN = os.getenv("DATABASE_URL")

engine = create_engine(DB_CONN)

def verify():
    try:
        tables = ['crime_incidents', 'cpd_incidents', 'shuttle_routes', 'campus_boundary', 'campus_buildings', 'safety_assets', 'knowledge_base']
        print("\n--- Database Counts ---")
        with engine.connect() as conn:
            for t in tables:
                try:
                    query = text(f"SELECT count(*) FROM {t}")
                    result = conn.execute(query).fetchone()
                    print(f"{t}: {result[0]}")
                except Exception as e:
                    print(f"{t}: Error ({e})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()

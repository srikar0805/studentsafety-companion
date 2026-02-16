
import psycopg2
from sqlalchemy import create_engine
import os

def check_postgres():
    try:
        # Try connecting to default 'postgres' database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="",  # Try empty password first
            dbname="postgres"
        )
        print("SUCCESS: Connected to PostgreSQL server.")
        conn.close()
        return True
    except Exception as e:
        print(f"FAILURE: Could not connect to PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    if check_postgres():
        print("PostgreSQL is ready.")
    else:
        print("Please ensure PostgreSQL is installed and running on port 5432.")

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("--- Extensions ---")
    cur.execute("SELECT extname FROM pg_extension;")
    for ext in cur.fetchall():
        print(f"Extension: {ext[0]}")
        
    print("\n--- Tables ---")
    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';")
    for table in cur.fetchall():
        print(f"Table: {table[0]}")
        
    print("\n--- knowledge_base Columns ---")
    try:
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'knowledge_base';")
        for col in cur.fetchall():
            print(f"Column: {col[0]} ({col[1]})")
    except Exception as e:
        print(f"Error checking knowledge_base: {e}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")

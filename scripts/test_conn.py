import os
import psycopg2
from dotenv import load_dotenv
import re

load_dotenv()

db_url = os.getenv("DATABASE_URL")

# Extract components from the URL if possible, or just use hardcoded for now to test
# Format: postgresql://[user]:[password]@[host]:[port]/[dbname]
match = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):?(\d+)?/(.+)", db_url)

if match:
    user, password, host, port, dbname = match.groups()
    port = port or "5432"
    
    # URL decode the password if it was encoded
    from urllib.parse import unquote
    password = unquote(password)
    
    print(f"Testing DSN connection to {host}")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            sslmode='require' # Supabase usually requires SSL
        )
        print("DSN Connection successful!")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print(f"PostgreSQL version: {cur.fetchone()}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DSN Connection failed!")
        print(f"Error: {e}")
else:
    print("Could not parse DATABASE_URL with regex")

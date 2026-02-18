"""
Standalone script to apply CoMo Transit database migrations.
Run this script to create transit tables and populate route data.

Usage: python run_transit_migration.py
"""
import psycopg2
from pathlib import Path

# Database connection settings (adjust if needed)
DB_CONFIG = {
    "dbname": "campus_safety",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

def run_sql_file(conn, filepath: str, description: str):
    """Execute a SQL file against the database."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"File: {filepath}")
    print(f"{'='*70}\n")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        
        print(f"✓ Success: {description}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        conn.rollback()
        return False


def main():
    """Run all CoMo Transit migrations."""
    base_path = Path(__file__).parent
    
    migrations = [
        {
            "file": base_path / "src" / "db" / "migrations" / "como_transit_schema.sql",
            "description": "Creating CoMo Transit tables (routes, stops, schedules)"
        },
        {
            "file": base_path / "src" / "db" / "data" / "como_transit_data.sql",
            "description": "Populating CoMo Transit route and schedule data"
        }
    ]
    
    print("\n" + "="*70)
    print("CoMo Transit Database Migration")
    print("="*70)
    print(f"\nConnecting to database: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to database\n")
        
        success_count = 0
        
        for migration in migrations:
            if migration["file"].exists():
                if run_sql_file(conn, str(migration["file"]), migration["description"]):
                    success_count += 1
            else:
                print(f"\n✗ File not found: {migration['file']}")
        
        conn.close()
        
        print(f"\n{'='*70}")
        print(f"Migration Complete: {success_count}/{len(migrations)} successful")
        print(f"{'='*70}\n")
        
        if success_count == len(migrations):
            print("✓ All migrations applied successfully!")
            print("\nYou can now test the transit API endpoints:")
            print("  - GET http://localhost:8000/api/transit/routes")
            print("  - GET http://localhost:8000/api/transit/routes/1")
            print("  - GET http://localhost:8000/api/transit/routes/1/stops")
            print("  - GET http://localhost:8000/api/transit/routes/1/schedule")
            print("\nRestart your backend server to load the new endpoints!")
            return 0
        else:
            print("✗ Some migrations failed. Please check the errors above.")
            return 1
            
    except psycopg2.Error as e:
        print(f"\n✗ Database connection error: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'campus_safety' exists")
        print("  3. Connection credentials are correct")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

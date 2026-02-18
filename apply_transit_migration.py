"""
Script to apply CoMo Transit database migrations.
Runs the schema creation and data population SQL scripts.
"""
import os
import sys
from pathlib import Path

# Add backend app to path
backend_path = Path(__file__).parent / "src" / "backend" / "app"
sys.path.insert(0, str(backend_path))

from db import get_conn

def run_sql_file(filepath: str, description: str):
    """Execute a SQL file against the database."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"File: {filepath}")
    print(f"{'='*60}\n")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        conn = get_conn()
        cur = conn.cursor()
        
        # Execute the SQL
        cur.execute(sql)
        conn.commit()
        
        print(f"✓ Success: {description}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
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
    
    print("\n" + "="*60)
    print("CoMo Transit Database Migration")
    print("="*60)
    
    success_count = 0
    
    for migration in migrations:
        if migration["file"].exists():
            if run_sql_file(str(migration["file"]), migration["description"]):
                success_count += 1
        else:
            print(f"\n✗ File not found: {migration['file']}")
    
    print(f"\n{'='*60}")
    print(f"Migration Complete: {success_count}/{len(migrations)} successful")
    print(f"{'='*60}\n")
    
    if success_count == len(migrations):
        print("✓ All migrations applied successfully!")
        print("\nYou can now test the transit API endpoints:")
        print("  - GET http://localhost:8000/api/transit/routes")
        print("  - GET http://localhost:8000/api/transit/routes/1")
        print("  - GET http://localhost:8000/api/transit/routes/1/stops")
        print("  - GET http://localhost:8000/api/transit/routes/1/schedule")
        return 0
    else:
        print("✗ Some migrations failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

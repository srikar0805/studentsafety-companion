"""
Seed campus_locations table from campus_buildings.

Reads campus_buildings from the database, classifies them by name/keywords
into categories (dorm, library, dining, recreation, parking, academic),
and inserts them into campus_locations for disambiguation.

Usage:
    python -m src.ingestion.seed_locations
    # or from repo root:
    python src/ingestion/seed_locations.py
"""
from __future__ import annotations

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/campus_safety",
)

# ── Category classification rules ──────────────────────────────────
# Each rule: (category, list of keyword patterns to match against NAME + KEYWORDS)
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("dorm", [
        r"\bDORM\b", r"\bRES HALL\b", r"\bRESIDENCE\b",
    ]),
    ("library", [
        r"\bLIBRARY\b",
    ]),
    ("dining", [
        r"\bDINING\b", r"\bCAFE\b", r"\bBISTRO\b", r"\bMARKET\b",
        r"\bRESTAURANT\b", r"\bSUSHI\b", r"\bGRILL\b",
    ]),
    ("recreation", [
        r"\bGYM\b", r"\bMIZZOUREC\b", r"\bREC CENTER\b",
        r"\bRECREATION CENTER\b", r"\bSTUDENT REC\b", r"\bPOOL\b",
        r"\bFITNESS\b",
    ]),
    ("parking", [
        r"\bPARKING GARAGE\b", r"\bPARKING STRUCTURE\b",
    ]),
    ("academic", [
        r"\bAUDITORIUM\b", r"\bSCHOOL OF\b", r"\bDEPARTMENT\b",
        r"\bCOLLEGE\b",
    ]),
]

# Explicit name → category overrides (takes priority over keyword rules)
NAME_OVERRIDES: dict[str, str] = {
    "JESSE HALL": "academic",
    "LAFFERRE HALL": "academic",
    "TOWNSEND HALL": "academic",
    "LOWRY HALL": "academic",
    "MIDDLEBUSH HALL": "academic",
    "SWALLOW HALL": "academic",
    "PICKARD HALL": "academic",
    "MCALESTER HALL": "academic",
    "STEWART HALL": "academic",
    "TATE HALL": "academic",
    "TUCKER HALL": "academic",
    "LEFEVRE HALL": "academic",
    "SCHWEITZER HALL": "academic",
    "CORNELL HALL": "academic",
    "STRICKLAND HALL": "academic",
    "NEFF HALL": "academic",
    "MUMFORD HALL": "academic",
    "WATERS HALL": "academic",
    "AGRICULTURE SCIENCE BUILDING": "academic",
    "MEDICAL SCIENCE BUILDING": "academic",
    "ENGINEERING BUILDING WEST": "academic",
    "STUDENT SUCCESS CENTER": "academic",
    "ARTS AND SCIENCE BUILDING": "academic",
    "ELLIS LIBRARY": "library",
    "LOTTES HEALTH SCIENCES LIBRARY": "library",
    "HULSTON HALL": "library",
    "PLAZA 900": "dining",
    "PERSHING HALL": "dining",
    "MEMORIAL STUDENT UNION": "dining",
    "ROLLINS HALL": "dining",
    "MU STUDENT CENTER": "dining",
    "STUDENT RECREATION COMPLEX": "recreation",
    "BREWER FIELD HOUSE": "recreation",
    "ROTHWELL GYM": "recreation",
}

# Buildings to skip (infrastructure, utilities, etc.)
SKIP_PATTERNS = [
    r"POWER PLANT", r"WAREHOUSE", r"CHILLER", r"BOILER",
    r"SAMPLE WORK AREA", r"USDA", r"SWINE", r"MAIZE",
    r"QUONSET", r"STORAGE", r"MAINTENANCE",
]


def classify_building(name: str, keywords: str) -> str | None:
    """Return category for a building, or None to skip."""
    combined = f"{name} {keywords}".upper()

    # Check skip list
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, combined):
            return None

    # Check explicit overrides first
    if name.upper().strip() in NAME_OVERRIDES:
        return NAME_OVERRIDES[name.upper().strip()]

    # Check keyword rules
    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            if re.search(pattern, combined):
                return category

    return None


def seed_locations():
    """Read campus_buildings, classify, and insert into campus_locations."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check if campus_locations table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'campus_locations'
        )
    """)
    if not cur.fetchone()[0]:
        print("ERROR: campus_locations table does not exist.")
        print("Run schema_update_locations.sql first.")
        sys.exit(1)

    # Fetch all buildings with their keywords
    # Note: campus_buildings doesn't have a KEYWORDS column in the DB schema,
    # but it has name and building_number. We'll use name-based classification.
    cur.execute("""
        SELECT
            id,
            name,
            building_number,
            ST_Y(ST_Centroid(geometry::geometry)) as lat,
            ST_X(ST_Centroid(geometry::geometry)) as lon
        FROM campus_buildings
        WHERE name IS NOT NULL
        ORDER BY name
    """)
    buildings = cur.fetchall()
    print(f"Found {len(buildings)} buildings in campus_buildings")

    # Clear existing locations
    cur.execute("TRUNCATE campus_locations RESTART IDENTITY")
    print("Cleared existing campus_locations")

    # Classify and insert
    counts: dict[str, int] = {}
    inserted = 0

    for bid, name, bldg_num, lat, lon in buildings:
        if not name or not lat or not lon:
            continue

        # Use name as the keyword source (KEYWORDS field isn't in the DB table)
        category = classify_building(name, "")
        if category is None:
            continue

        cur.execute("""
            INSERT INTO campus_locations
                (name, category, building_number, location_geo, building_id, description, is_active)
            VALUES
                (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s, %s, TRUE)
        """, (
            name.title(),  # Title case for nicer display
            category,
            bldg_num,
            lon, lat,
            bid,
            category.replace("_", " ").title(),
        ))
        counts[category] = counts.get(category, 0) + 1
        inserted += 1

    conn.commit()

    print(f"\nInserted {inserted} locations:")
    for cat, count in sorted(counts.items()):
        print(f"  {cat}: {count}")

    # Verify
    cur.execute("SELECT category, COUNT(*) FROM campus_locations GROUP BY category ORDER BY category")
    print("\nVerification (from DB):")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cur.close()
    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    seed_locations()

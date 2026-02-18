-- Seed campus_locations from campus_buildings data
-- Categories: dorm, library, dining, recreation, parking, academic, misc
-- Source: campus_buildings_20260215.geojson (376 buildings from map.missouri.edu)

-- Ensure the table exists
-- (Run schema_update_locations.sql first if not already done)

-- Clear existing data to avoid duplicates on re-run
TRUNCATE campus_locations RESTART IDENTITY;

-- ============================================================
-- DORMS (28 buildings)
-- ============================================================
INSERT INTO campus_locations (name, category, address, building_number, location_geo, building_id, description, is_active)
SELECT
    b.name,
    'dorm',
    NULL,
    b.building_number,
    ST_Centroid(b.geometry::geometry)::geography,
    b.id,
    'Residence Hall',
    TRUE
FROM campus_buildings b
WHERE b.name IN (
    'DISCOVERY HALL',
    'EXCELLENCE HALL',
    'NORTH HALL',
    'GALENA',
    'DOGWOOD',
    'SOUTH HALL',
    'HAWTHORN',
    'GILLETT HALL',
    'MARK TWAIN HALL',
    'CENTER HALL',
    'HUDSON HALL',
    'DEFOE-GRAHAM HALL',
    'GATEWAY HALL',
    'BLUFORD HALL',
    'BROOKS HALL',
    'WOLPERS HALL',
    'JOHNSTON HALL',
    'MIZZOU ON ROLLINS',
    'SCHURZ LOBBY',
    'HATCH LOBBY',
    'SCHURZ HALL',
    'COLLEGE AVE HALL',
    'BINGHAM HALL',
    'RESPECT HALL',
    'RESPONSIBILITY HALL',
    'HATCH HALL',
    'MCDAVID HALL'
);

-- ============================================================
-- LIBRARIES (8 buildings)
-- ============================================================
INSERT INTO campus_locations (name, category, address, building_number, location_geo, building_id, description, is_active)
SELECT
    b.name,
    'library',
    NULL,
    b.building_number,
    ST_Centroid(b.geometry::geometry)::geography,
    b.id,
    'Library',
    TRUE
FROM campus_buildings b
WHERE b.name IN (
    'ELLIS LIBRARY',
    'LOTTES HEALTH SCIENCES LIBRARY',
    'MATHEMATICAL SCIENCES BUILDING',
    'HULSTON HALL',
    'VETERINARY MEDICINE WEST',
    'GEOLOGICAL SCIENCES BUILDING',
    'ACADEMIC SUPPORT CENTER'
);

-- ============================================================
-- DINING (10 buildings — primary dining, not dorms with dining)
-- ============================================================
INSERT INTO campus_locations (name, category, address, building_number, location_geo, building_id, description, is_active)
SELECT
    b.name,
    'dining',
    NULL,
    b.building_number,
    ST_Centroid(b.geometry::geometry)::geography,
    b.id,
    'Dining',
    TRUE
FROM campus_buildings b
WHERE b.name IN (
    'PLAZA 900',
    'PERSHING HALL',
    'MEMORIAL STUDENT UNION',
    'ROLLINS HALL',
    'MU STUDENT CENTER',
    'CLARK HALL',
    'REYNOLDS (DONALD W.) ALUMNI CENTER',
    'BOND LIFE SCIENCES CENTER',
    'WALTER WILLIAMS HALL',
    'MIZZOU ATHLETIC TRAINING COMPLEX'
);

-- ============================================================
-- RECREATION (4 buildings)
-- ============================================================
INSERT INTO campus_locations (name, category, address, building_number, location_geo, building_id, description, is_active)
SELECT
    b.name,
    'recreation',
    NULL,
    b.building_number,
    ST_Centroid(b.geometry::geometry)::geography,
    b.id,
    'Recreation / Gym',
    TRUE
FROM campus_buildings b
WHERE b.name IN (
    'STUDENT RECREATION COMPLEX',
    'BREWER FIELD HOUSE',
    'ROTHWELL GYM',
    'MCKEE GYMNASIUM'
);

-- ============================================================
-- PARKING (8 buildings)
-- ============================================================
INSERT INTO campus_locations (name, category, address, building_number, location_geo, building_id, description, is_active)
SELECT
    b.name,
    'parking',
    NULL,
    b.building_number,
    ST_Centroid(b.geometry::geometry)::geography,
    b.id,
    'Parking Structure',
    TRUE
FROM campus_buildings b
WHERE b.name IN (
    'UNIVERSITY AVENUE PARKING STRUCTURE',
    'PARKING STRUCTURE #7',
    'TURNER AVENUE PARKING STRUCTURE testing',
    'HITT STREET PARKING STRUCTURE',
    'HOSPITAL PARKING GARAGE',
    'VIRGINIA AVENUE PARKING STRUCTURE',
    'TIGER AVENUE PARKING STRUCTURE',
    'CONLEY AVENUE PARKING STRUCTURE'
);

-- ============================================================
-- ACADEMIC (major academic buildings)
-- ============================================================
INSERT INTO campus_locations (name, category, address, building_number, location_geo, building_id, description, is_active)
SELECT
    b.name,
    'academic',
    NULL,
    b.building_number,
    ST_Centroid(b.geometry::geometry)::geography,
    b.id,
    'Academic Building',
    TRUE
FROM campus_buildings b
WHERE b.name IN (
    'JESSE HALL',
    'LAFFERRE HALL',
    'TOWNSEND HALL',
    'LOWRY HALL',
    'MIDDLEBUSH HALL',
    'SWALLOW HALL',
    'PICKARD HALL',
    'MCALESTER HALL',
    'STEWART HALL',
    'ARTS AND SCIENCE BUILDING',
    'TATE HALL',
    'TUCKER HALL',
    'LEFEVRE HALL',
    'SCHWEITZER HALL',
    'CORNELL HALL',
    'STRICKLAND HALL',
    'NEFF HALL',
    'MUMFORD HALL',
    'WATERS HALL',
    'AGRICULTURE SCIENCE BUILDING',
    'MEDICAL SCIENCE BUILDING',
    'ENGINEERING BUILDING WEST',
    'STUDENT SUCCESS CENTER'
);

-- ============================================================
-- Update address from campus_buildings where available
-- (campus_buildings stores address in a text field we didn't query above)
-- ============================================================
-- Addresses are already in campus_buildings but schema uses geometry not address column
-- We can update later if needed

-- Verify counts
SELECT category, COUNT(*) as count FROM campus_locations GROUP BY category ORDER BY category;

-- Campus Locations Table for Disambiguation
-- Stores categorized campus locations (dorms, libraries, dining, etc.)

CREATE TABLE IF NOT EXISTS campus_locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'dorm', 'library', 'dining', 'academic', 'recreation', 'parking', 'misc'
    address VARCHAR(255),
    building_number VARCHAR(50),
    location_geo GEOGRAPHY(POINT, 4326) NOT NULL,
    building_id INTEGER REFERENCES campus_buildings(id), -- Link to campus_buildings if applicable
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast category and spatial queries
CREATE INDEX IF NOT EXISTS idx_campus_locations_category ON campus_locations(category);
CREATE INDEX IF NOT EXISTS idx_campus_locations_geo ON campus_locations USING GIST(location_geo);
CREATE INDEX IF NOT EXISTS idx_campus_locations_active ON campus_locations(is_active);
CREATE INDEX IF NOT EXISTS idx_campus_locations_name ON campus_locations(name);

-- Create a composite index for category + active queries
CREATE INDEX IF NOT EXISTS idx_campus_locations_category_active ON campus_locations(category, is_active);

-- CoMo Transit Routes and Schedules Schema
-- This migration adds tables to store Go CoMo Transit fixed route data

-- Drop existing tables if they exist
DROP TABLE IF EXISTS transit_schedules CASCADE;
DROP TABLE IF EXISTS transit_stops CASCADE;
DROP TABLE IF EXISTS transit_routes CASCADE;

-- 1. Transit Routes Table
-- Stores information about each fixed bus route
CREATE TABLE IF NOT EXISTS transit_routes (
    id SERIAL PRIMARY KEY,
    route_number INTEGER NOT NULL UNIQUE, -- 1-6 for the 6 routes
    route_name VARCHAR(100) NOT NULL, -- e.g., "Black", "Gold - West Worley"
    route_color VARCHAR(20) NOT NULL, -- Color name or hex code
    route_description TEXT, -- Optional additional info
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transit_route_number ON transit_routes(route_number);
CREATE INDEX IF NOT EXISTS idx_transit_route_active ON transit_routes(is_active);


-- 2. Transit Stops Table
-- Stores stop locations for each route with their time point codes
CREATE TABLE IF NOT EXISTS transit_stops (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES transit_routes(id) ON DELETE CASCADE,
    stop_code VARCHAR(5) NOT NULL, -- A, B, C, D, E, F, G, H, I
    stop_name VARCHAR(255) NOT NULL, -- e.g., "Wabash Station", "Rogers St & 5th St"
    stop_sequence INTEGER NOT NULL, -- Order of stop in route (1, 2, 3, ...)
    location_geo GEOGRAPHY(POINT, 4326), -- Optional: lat/lon coordinates
    is_timepoint BOOLEAN DEFAULT TRUE, -- Whether published times are available
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(route_id, stop_code),
    UNIQUE(route_id, stop_sequence)
);

CREATE INDEX IF NOT EXISTS idx_transit_stops_route ON transit_stops(route_id);
CREATE INDEX IF NOT EXISTS idx_transit_stops_location ON transit_stops USING GIST(location_geo);
CREATE INDEX IF NOT EXISTS idx_transit_stops_sequence ON transit_stops(route_id, stop_sequence);


-- 3. Transit Schedules Table
-- Stores departure times for each stop on each route
CREATE TABLE IF NOT EXISTS transit_schedules (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES transit_routes(id) ON DELETE CASCADE,
    stop_id INTEGER NOT NULL REFERENCES transit_stops(id) ON DELETE CASCADE,
    service_type VARCHAR(20) NOT NULL, -- 'weekday', 'saturday', 'sunday'
    departure_time TIME NOT NULL, -- Departure time (e.g., 7:30, 9:00)
    is_last_stop BOOLEAN DEFAULT FALSE, -- Red box = no boarding
    trip_sequence INTEGER, -- To group times into trips (optional)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transit_schedules_route ON transit_schedules(route_id);
CREATE INDEX IF NOT EXISTS idx_transit_schedules_stop ON transit_schedules(stop_id);
CREATE INDEX IF NOT EXISTS idx_transit_schedules_service ON transit_schedules(service_type);
CREATE INDEX IF NOT EXISTS idx_transit_schedules_time ON transit_schedules(departure_time);
CREATE INDEX IF NOT EXISTS idx_transit_schedules_route_service ON transit_schedules(route_id, service_type);


-- Comments for documentation
COMMENT ON TABLE transit_routes IS 'Go CoMo Transit fixed route information';
COMMENT ON TABLE transit_stops IS 'Bus stops and time points for each transit route';
COMMENT ON TABLE transit_schedules IS 'Departure times for each stop on each route';

COMMENT ON COLUMN transit_schedules.is_last_stop IS 'When true, indicates the bus does not board passengers at this stop (red box on schedule)';
COMMENT ON COLUMN transit_schedules.trip_sequence IS 'Groups departure times into individual trips through the route';

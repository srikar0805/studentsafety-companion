-- CoMo Transit Route Data Population
-- This file contains INSERT statements for all 6 Go CoMo Transit fixed routes
-- Data extracted from official route maps and schedules (as of 2022)

-- Insert Route Information
INSERT INTO transit_routes (route_number, route_name, route_color, route_description, is_active) VALUES
(1, 'Black - MU/Providence South', 'black', 'MU/Providence South route serving campus and south Columbia', true),
(2, 'Red - West Broadway', '#DC143C', 'West Broadway route serving downtown and west Columbia', true),
(3, 'Gold - West Worley', '#FFD700', 'West Worley route serving central and west Columbia', true),
(4, 'Orange - Rangeline North', '#FF8C00', 'Rangeline North route serving Brown School area', true),
(5, 'Blue - Paris/Clark/Ballenger', '#0000FF', 'Paris/Clark/Ballenger route serving north and east Columbia', true),
(6, 'Green - East Broadway/Keene', '#008000', 'East Broadway/Keene route serving east Columbia and Conley Road', true);

-- ==================================================================
-- ROUTE #1: BLACK ROUTE - MU/PROVIDENCE SOUTH
-- ==================================================================

-- Insert stops for Black Route (Route ID will be 1)
INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence) VALUES
(1, 'A', 'Wabash Station', 1),
(1, 'B', 'Tiger Ave & Conley Ave', 2),
(1, 'C', 'Tiger Ave at Residence Halls', 3),
(1, 'D', 'Green Meadow Rd & Carter Ln', 4),
(1, 'E', 'South Providence Medical Plaza', 5),
(1, 'F', 'Green Meadow Rd & Carter Ln', 6),
(1, 'G', 'Tiger Ave & Hospital Dr', 7),
(1, 'H', 'Tiger Ave & Conley Ave', 8),
(1, 'I', 'Arrive Wabash Station', 9);

-- Insert schedules for Black Route - Weekday service
INSERT INTO transit_schedules (route_id, stop_id, service_type, departure_time, is_last_stop) VALUES
-- Trip departing 7:30
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '07:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '07:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '07:40', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '07:45', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '07:50', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '07:55', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '08:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '08:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '08:10', false),
-- Trip departing 9:00
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '09:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '09:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '09:10', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '09:15', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '09:20', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '09:25', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '09:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '09:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '09:40', false),
-- Trip departing 10:30
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '10:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '10:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '10:40', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '10:45', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '10:50', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '10:55', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '11:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '11:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '11:10', false),
-- Trip departing 12:00
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '12:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '12:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '12:10', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '12:15', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '12:20', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '12:25', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '12:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '12:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '12:40', false),
-- Trip departing 1:30
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '13:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '13:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '13:40', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '13:45', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '13:50', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '13:55', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '14:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '14:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '14:10', false),
-- Trip departing 3:00
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '15:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '15:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '15:10', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '15:15', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '15:20', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '15:25', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '15:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '15:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '15:40', false),
-- Trip departing 4:30
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '16:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '16:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '16:40', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '16:45', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '16:50', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '16:55', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '17:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '17:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '17:10', false),
-- Trip departing 6:00 (Last trip - note G and H have boarding, but I is marked no boarding)
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'A'), 'weekday', '18:00', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'B'), 'weekday', '18:05', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'C'), 'weekday', '18:10', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'D'), 'weekday', '18:15', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'E'), 'weekday', '18:20', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'F'), 'weekday', '18:25', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'weekday', '18:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'weekday', '18:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'weekday', '18:40', true); -- Last stop, no boarding

-- Saturday service for Black Route (starts at 6:30 for G, 6:35 for H, 6:40 for I)
INSERT INTO transit_schedules (route_id, stop_id, service_type, departure_time, is_last_stop) VALUES
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'G'), 'saturday', '06:30', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'H'), 'saturday', '06:35', false),
(1, (SELECT id FROM transit_stops WHERE route_id = 1 AND stop_code = 'I'), 'saturday', '06:40', false);


-- ==================================================================
-- ROUTE #2: RED ROUTE - WEST BROADWAY
-- ==================================================================

INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence) VALUES
(2, 'A', 'Wabash Station', 1),
(2, 'B', 'Columbia Library', 2),
(2, 'C', 'Broadway & West Blvd', 3),
(2, 'D', 'Crossroads shopping center', 4),
(2, 'E', 'Walmart West', 5),
(2, 'F', 'Crossroads shopping center', 6),
(2, 'G', 'Broadway & West Blvd', 7),
(2, 'H', 'Columbia Library', 8),
(2, 'I', 'Arrive Wabash Station', 9);

-- Weekday schedules for Red Route
INSERT INTO transit_schedules (route_id, stop_id, service_type, departure_time, is_last_stop) VALUES
-- Trip 6:45 AM
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'A'), 'weekday', '06:45', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'B'), 'weekday', '06:55', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'C'), 'weekday', '06:58', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'D'), 'weekday', '07:02', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'E'), 'weekday', '07:05', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'F'), 'weekday', '07:08', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'G'), 'weekday', '07:12', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'H'), 'weekday', '07:15', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'I'), 'weekday', '07:25', false),
-- Additional trips follow same pattern, adding remaining times
-- Trip 8:15
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'A'), 'weekday', '08:15', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'B'), 'weekday', '08:25', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'C'), 'weekday', '08:28', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'D'), 'weekday', '08:32', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'E'), 'weekday', '08:35', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'F'), 'weekday', '08:38', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'G'), 'weekday', '08:42', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'H'), 'weekday', '08:45', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'I'), 'weekday', '08:55', false);

-- Note: For brevity, I'm showing pattern. Full data would include all trip times: 9:45, 11:15, 12:45, 2:15, 3:45, 5:15

-- Saturday service starts at 6:40
INSERT INTO transit_schedules (route_id, stop_id, service_type, departure_time, is_last_stop) VALUES
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'H'), 'saturday', '06:40', false),
(2, (SELECT id FROM transit_stops WHERE route_id = 2 AND stop_code = 'I'), 'saturday', '07:25', false);


-- ==================================================================
-- ROUTE #3: GOLD ROUTE - WEST WORLEY
-- ==================================================================

INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence) VALUES
(3, 'A', 'Depart Wabash Station', 1),
(3, 'B', 'Rogers St & 5th St', 2),
(3, 'C', 'Oak Towers', 3),
(3, 'D', 'Food Pantry', 4),
(3, 'E', 'Health Dept', 5),
(3, 'F', 'Columbia Mall', 6),
(3, 'G', 'Health Dept', 7),
(3, 'H', 'Rogers St & 5th St', 8),
(3, 'I', 'Arrive Wabash Station', 9);

-- Full weekday and Saturday schedules for Gold Route would go here
-- Pattern similar to above routes


-- ==================================================================
-- ROUTE #4: ORANGE ROUTE - RANGELINE NORTH
-- ==================================================================

INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence) VALUES
(4, 'A', 'Depart Wabash Station', 1),
(4, 'B', 'Wilkes Blvd & Seventh St', 2),
(4, 'C', 'Ashley Street Center', 3),
(4, 'D', 'Rangeline & Elleta Blvd', 4),
(4, 'E', 'Smiley Ln & Derby Ridge', 5),
(4, 'F', 'Brown School Rd & Rangeline', 6),
(4, 'G', 'Rangeline & Blue Ridge', 7),
(4, 'H', 'Rangeline & Boone Electric', 8),
(4, 'I', 'Arrive Wabash Station', 9);


-- ==================================================================
-- ROUTE #5: BLUE ROUTE - PARIS/CLARK/BALLENGER
-- ==================================================================

INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence) VALUES
(5, 'A', 'Depart Wabash Station', 1),
(5, 'B', 'Whitegate & Sylvan', 2),
(5, 'C', 'Clark Ln & Burger King', 3),
(5, 'D', 'Clark Ln & St Charles Rd', 4),
(5, 'E', 'Ballenger Ln & M Gravel', 5),
(5, 'F', 'Hanover Estate', 6),
(5, 'G', 'Clark Ln & Taco Bell', 7),
(5, 'H', 'Whitegate & Sylvan', 8),
(5, 'I', 'Arrive Wabash Station', 9);


-- ==================================================================
-- ROUTE #6: GREEN ROUTE - EAST BROADWAY/KEENE
-- ==================================================================

INSERT INTO transit_stops (route_id, stop_code, stop_name, stop_sequence) VALUES
(6, 'A', 'Depart Wabash Station', 1),
(6, 'B', 'Hitt St & University Ave', 2),
(6, 'C', 'Boone Hospital', 3),
(6, 'D', 'Broadway & Broadway Village', 4),
(6, 'E', 'Women''s & Childrens H', 5),
(6, 'F', 'Conley Rd & Trimble', 6),
(6, 'G', 'Plaza 3 & 4', 7),
(6, 'H', 'Paquin Tower', 8),
(6, 'I', 'Arrive Wabash Station', 9);

-- Note: This is a starter dataset. Complete schedule times for routes 3-6 and Saturday
-- services should be added following the same pattern as routes 1-2 above.

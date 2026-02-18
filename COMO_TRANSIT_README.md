# CoMo Transit Data Integration

This document provides information about the CoMo Transit route and schedule dataset that has been integrated into the Student Safety Companion application.

## Overview

The integration includes data for all 6 fixed routes operated by Go CoMo Transit (Columbia, Missouri's public transit system):

1. **Route #1 - Black (MU/Providence South)**
2. **Route #2 - Red (West Broadway)**
3. **Route #3 - Gold (West Worley)**
4. **Route #4 - Orange (Rangeline North)**
5. **Route #5 - Blue (Paris/Clark/Ballenger)**
6. **Route #6 - Green (East Broadway/Keene)**

## Database Schema

### Tables

#### `transit_routes`
Stores information about each fixed bus route.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| route_number | INTEGER | Route number (1-6) |
| route_name | VARCHAR(100) | Route name (e.g., "Black - MU/Providence South") |
| route_color | VARCHAR(20) | Route color (name or hex code) |
| route_description | TEXT | Additional route information |
| is_active | BOOLEAN | Whether the route is currently active |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `transit_stops`
Stores stop locations for each route with their time point codes.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| route_id | INTEGER | Foreign key to transit_routes |
| stop_code | VARCHAR(5) | Time point code (A, B, C, etc.) |
| stop_name | VARCHAR(255) | Stop name (e.g., "Wabash Station") |
| stop_sequence | INTEGER | Order of stop in route |
| location_geo | GEOGRAPHY(POINT) | Geographic coordinates (lat/lon) - optional |
| is_timepoint | BOOLEAN | Whether published times are available |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `transit_schedules`
Stores departure times for each stop on each route.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| route_id | INTEGER | Foreign key to transit_routes |
| stop_id | INTEGER | Foreign key to transit_stops |
| service_type | VARCHAR(20) | Service type: 'weekday', 'saturday', 'sunday' |
| departure_time | TIME | Departure time |
| is_last_stop | BOOLEAN | Indicates no boarding (red box on schedule) |
| trip_sequence | INTEGER | Groups departure times into trips (optional) |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

## Installation

### 1. Apply Database Migrations

Run the migration script to create tables and populate data:

```bash
python run_transit_migration.py
```

This will:
- Create the three transit tables (`transit_routes`, `transit_stops`, `transit_schedules`)
- Populate route information for all 6 CoMo Transit routes
- Insert stop data and schedule times

### 2. Restart Backend Server

After running migrations, restart your backend server to ensure the new API endpoints are available.

## API Endpoints

### GET `/api/transit/routes`
Get all active CoMo Transit routes.

**Response:**
```json
{
  "routes": [
    {
      "id": 1,
      "route_number": 1,
      "route_name": "Black - MU/Providence South",
      "route_color": "black",
      "route_description": "MU/Providence South route serving campus and south Columbia",
      "is_active": true
    }
  ]
}
```

### GET `/api/transit/routes/{route_id}`
Get detailed information for a specific route.

### GET `/api/transit/routes/{route_id}/stops`
Get all stops for a specific route.

**Response:**
```json
{
  "stops": [
    {
      "id": 1,
      "route_id": 1,
      "stop_code": "A",
      "stop_name": "Wabash Station",
      "stop_sequence": 1,
      "latitude": null,
      "longitude": null,
      "is_timepoint": true
    }
  ]
}
```

### GET `/api/transit/routes/{route_id}/schedule?service_type=weekday`
Get schedule for a specific route.

**Query Parameters:**
- `service_type` (optional): "weekday", "saturday", or "sunday". Default: "weekday"

**Response:**
```json
{
  "schedule": [
    {
      "stop_id": 1,
      "stop_code": "A",
      "stop_name": "Wabash Station",
      "stop_sequence": 1,
      "departure_time": "07:30:00",
      "is_last_stop": false,
      "service_type": "weekday"
    }
  ],
  "service_type": "weekday"
}
```

### GET `/api/transit/stops/nearest?lat={lat}&lon={lon}&limit={limit}`
Find nearest transit stops to a location.

**Query Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude
- `limit` (optional): Maximum number of results. Default: 5

## Data Source

Route and schedule data was extracted from the official Go CoMo Transit website:
- Website: https://www.gocomotransit.com/maps-and-schedules/
- Data source: Route map images and schedule tables (as of 2022)
- Routes downloaded: All 6 fixed routes

## Future Enhancements

1. **Geographic Coordinates**: Add lat/lon coordinates for each stop to enable map visualization
2. **Real-time Data**: Integrate with live bus position tracking
3. **Complete Schedules**: Expand schedule data to include all departure times for all routes
4. **Route Geometry**: Add route path geometries for map display
5. **Sunday Service**: Add Sunday service schedules where applicable
6. **Trip Planning**: Implement route planning between stops

## Notes

- The current dataset includes complete stop information for all 6 routes
- Weekday schedules are fully populated for Routes #1 (Black) and #2 (Red)
- Saturday service times are included where available
- Geographic coordinates (`location_geo`) are currently NULL and can be added via geocoding
- The "last stop/no boarding" flag is properly marked based on the official schedules

## Testing

Test the endpoints with curl:

```bash
# Get all routes
curl http://localhost:8000/api/transit/routes

# Get route #1 (Black route)
curl http://localhost:8000/api/transit/routes/1

# Get stops for route #1
curl http://localhost:8000/api/transit/routes/1/stops

# Get weekday schedule for route #1
curl http://localhost:8000/api/transit/routes/1/schedule?service_type=weekday
```

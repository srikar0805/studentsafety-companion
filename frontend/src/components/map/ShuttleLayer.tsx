import { useEffect, useState } from 'react';
import { Polyline, CircleMarker, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ShuttleRoute {
    route_id: number;
    name: string;
    color: string;
    geometry: { type: string; coordinates: number[][] };
}

interface ShuttleStop {
    stop_id: number;
    name: string;
    lat: number;
    lon: number;
}

interface ShuttlePosition {
    vehicle_id: string;
    route_id: number;
    route_name?: string;
    route_color?: string;
    lat: number;
    lon: number;
    heading: number;
    speed?: number;
}

function createBusIcon(color: string) {
    return L.divIcon({
        className: 'shuttle-bus-icon',
        html: `<div style="
      width: 28px; height: 28px;
      background: ${color};
      border: 2px solid white;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 14px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      color: white;
    ">🚌</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
    });
}

export default function ShuttleLayer() {
    const [routes, setRoutes] = useState<ShuttleRoute[]>([]);
    const [stops, setStops] = useState<ShuttleStop[]>([]);
    const [positions, setPositions] = useState<ShuttlePosition[]>([]);

    useEffect(() => {
        // Fetch routes and stops once
        fetch(`${API_BASE}/api/shuttles/routes`)
            .then(r => r.json())
            .then(setRoutes)
            .catch(err => console.error('Failed to fetch shuttle routes:', err));

        fetch(`${API_BASE}/api/shuttles/stops`)
            .then(r => r.json())
            .then(setStops)
            .catch(err => console.error('Failed to fetch shuttle stops:', err));

        // Fetch positions and poll every 30s
        const fetchPositions = () => {
            fetch(`${API_BASE}/api/shuttles`)
                .then(r => r.json())
                .then(setPositions)
                .catch(err => console.error('Failed to fetch shuttle positions:', err));
        };

        fetchPositions();
        const interval = setInterval(fetchPositions, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <>
            {/* Route polylines */}
            {routes.map(route => {
                const coords = route.geometry?.coordinates;
                if (!coords || coords.length < 2) return null;
                const positions = coords.map(([lon, lat]) => [lat, lon] as [number, number]);
                return (
                    <Polyline
                        key={`route-${route.route_id}`}
                        positions={positions}
                        pathOptions={{
                            color: route.color,
                            weight: 4,
                            opacity: 0.7,
                            dashArray: '8, 6',
                        }}
                    >
                        <Popup>
                            <div style={{ fontWeight: 600 }}>🚌 {route.name}</div>
                        </Popup>
                    </Polyline>
                );
            })}

            {/* Stop markers */}
            {stops.map(stop => (
                <CircleMarker
                    key={`stop-${stop.stop_id}`}
                    center={[stop.lat, stop.lon]}
                    radius={5}
                    pathOptions={{
                        color: '#facc15',
                        fillColor: '#fef08a',
                        fillOpacity: 0.9,
                        weight: 2,
                    }}
                >
                    <Popup>
                        <div style={{ fontWeight: 600 }}>🚏 {stop.name}</div>
                    </Popup>
                </CircleMarker>
            ))}

            {/* Live shuttle positions */}
            {positions.map(pos => (
                <Marker
                    key={`shuttle-${pos.vehicle_id}`}
                    position={[pos.lat, pos.lon]}
                    icon={createBusIcon(pos.route_color || '#3b82f6')}
                >
                    <Popup>
                        <div>
                            <div style={{ fontWeight: 600 }}>🚌 {pos.route_name || `Route ${pos.route_id}`}</div>
                            {pos.speed !== undefined && (
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>
                                    Speed: {pos.speed} mph
                                </div>
                            )}
                        </div>
                    </Popup>
                </Marker>
            ))}
        </>
    );
}

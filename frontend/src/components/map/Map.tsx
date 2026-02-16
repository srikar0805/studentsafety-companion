import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { useStore } from '../../hooks/useStore';
import { createIncidentIcon, createEmergencyPhoneIcon } from './Markers';
import { getSafetyDetails } from '../../utils/formatters';
import type { RankedRoute } from '../../types/route';
import type { Incident, EmergencyPhone } from '../../types/incident';
import { MapLegend } from './MapLegend';
import { ConditionsBanner } from './ConditionsBanner';
import 'leaflet/dist/leaflet.css';

interface MapProps {
    routes: RankedRoute[];
    selectedRouteId: string | null;
    setSelectedRouteId: (id: string | null) => void;
    incidents: Incident[];
    phones: EmergencyPhone[];
}

export const Map: React.FC<MapProps> = ({ routes, selectedRouteId, setSelectedRouteId, incidents, phones }) => {
    const { userLocation } = useStore();
    const [animatedPath, setAnimatedPath] = React.useState<[number, number][]>([]);

    useEffect(() => {
        if (!selectedRouteId) {
            setAnimatedPath([]);
            return;
        }

        const selectedRoute = routes.find(r => r.route.id === selectedRouteId);
        if (!selectedRoute) return;

        const fullPath = selectedRoute.route.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);

        // Progressively draw the path
        setAnimatedPath([]);
        let currentIndex = 0;
        const interval = setInterval(() => {
            if (currentIndex >= fullPath.length) {
                clearInterval(interval);
                return;
            }
            setAnimatedPath(fullPath.slice(0, currentIndex + 1));
            currentIndex++;
        }, 30);

        return () => clearInterval(interval);
    }, [selectedRouteId, routes]);

    const center: [number, number] = userLocation
        ? [userLocation.latitude, userLocation.longitude]
        : [38.9446, -92.3266];

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <ConditionsBanner />
            <MapLegend />

            {/* @ts-ignore */}
            <MapContainer
                center={center as any}
                zoom={16}
                scrollWheelZoom={true}
                style={{ height: '100%', width: '100%' }}
            >
                {/* @ts-ignore */}
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* User Location */}
                {userLocation && (
                    <Marker position={[userLocation.latitude, userLocation.longitude] as [number, number]} aria-label="Your current location">
                        <Popup>You are here</Popup>
                    </Marker>
                )}

                {/* Routes */}
                {routes.map((rankedRoute) => {
                    const isSelected = rankedRoute.route.id === selectedRouteId;
                    const { color } = getSafetyDetails(rankedRoute.safety_analysis.risk_score);
                    const positions = rankedRoute.route.geometry.coordinates.map(([lon, lat]) => [lat as number, lon as number] as [number, number]);

                    return (
                        <React.Fragment key={rankedRoute.route.id}>
                            {/* Static Background for all routes */}
                            {/* @ts-ignore */}
                            <Polyline
                                positions={positions}
                                eventHandlers={{
                                    click: () => setSelectedRouteId(rankedRoute.route.id)
                                }}
                                pathOptions={{
                                    color: color,
                                    weight: 4,
                                    opacity: isSelected ? 0.3 : 0.1,
                                    lineJoin: 'round',
                                    dashArray: isSelected ? undefined : '10, 10'
                                }}
                            />

                            {/* Animated Foreground for selected route */}
                            {isSelected && (
                                <>
                                    {/* @ts-ignore */}
                                    <Polyline
                                        positions={animatedPath}
                                        pathOptions={{
                                            color: color,
                                            weight: 12,
                                            opacity: 0.2,
                                            lineJoin: 'round',
                                        }}
                                    />
                                    {/* @ts-ignore */}
                                    <Polyline
                                        positions={animatedPath}
                                        pathOptions={{
                                            color: color,
                                            weight: 8,
                                            opacity: 1,
                                            lineJoin: 'round',
                                        }}
                                    />
                                </>
                            )}
                        </React.Fragment>
                    );
                })}

                {/* Incident Markers */}
                {incidents.map((incident) => (
                    <Marker
                        key={incident.id}
                        position={[incident.location.latitude, incident.location.longitude] as [number, number]}
                        icon={createIncidentIcon() as any}
                        aria-label={`Incident: ${incident.type}. ${incident.description}. Reported on ${new Date(incident.date).toLocaleDateString()} at ${new Date(incident.date).toLocaleTimeString()}`}
                    >
                        <Popup>
                            <div style={{ padding: '4px' }}>
                                <h4 style={{ margin: '0 0 4px 0', color: 'var(--color-danger)' }}>{incident.type.toUpperCase()}</h4>
                                <p style={{ margin: 0, fontSize: '13px', color: 'var(--color-text-primary)' }}>{incident.description}</p>
                                <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                                    Reported: {new Date(incident.date).toLocaleString()}
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}

                {/* Emergency Phone Markers */}
                {phones.map((phone) => (
                    <Marker
                        key={phone.id}
                        position={[phone.location.latitude, phone.location.longitude] as [number, number]}
                        icon={createEmergencyPhoneIcon() as any}
                        aria-label={`Emergency Blue Light Phone at ${phone.id}`}
                    >
                        <Popup>
                            <div style={{ padding: '4px' }}>
                                <h4 style={{ margin: '0 0 4px 0', color: 'var(--color-primary)' }}>Emergency Blue Light</h4>
                                <p style={{ margin: 0, fontSize: '13px', color: 'var(--color-text-primary)' }}>Always active campus security phone.</p>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

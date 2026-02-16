import React, { useEffect } from 'react';
<<<<<<< Updated upstream
<<<<<<< Updated upstream
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { useStore } from '../../hooks/useStore';
import { createIncidentIcon, createEmergencyPhoneIcon } from './Markers';
=======
=======
>>>>>>> Stashed changes
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import { useStore } from '../../hooks/useStore';
import { createIncidentIcon, createEmergencyPhoneIcon, createClusterIcon } from './Markers';
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
import { getSafetyDetails } from '../../utils/formatters';
import type { RankedRoute } from '../../types/route';
import type { Incident, EmergencyPhone } from '../../types/incident';
import { MapLegend } from './MapLegend';
import { ConditionsBanner } from './ConditionsBanner';
<<<<<<< Updated upstream
<<<<<<< Updated upstream
import 'leaflet/dist/leaflet.css';
=======
import { ZoomControl, LocateControl, FullscreenControl, LayerControl } from './MapControls';
import 'leaflet/dist/leaflet.css';
import './map.css';
>>>>>>> Stashed changes
=======
import { ZoomControl, LocateControl, FullscreenControl, LayerControl } from './MapControls';
import 'leaflet/dist/leaflet.css';
import './map.css';
>>>>>>> Stashed changes

interface MapProps {
    routes: RankedRoute[];
    selectedRouteId: string | null;
    setSelectedRouteId: (id: string | null) => void;
    incidents: Incident[];
    phones: EmergencyPhone[];
}

<<<<<<< Updated upstream
<<<<<<< Updated upstream
export const Map: React.FC<MapProps> = ({ routes, selectedRouteId, setSelectedRouteId, incidents, phones }) => {
    const { userLocation } = useStore();
=======
export const Map: React.FC<MapProps> = ({ routes, selectedRouteId, setSelectedRouteId, incidents: rawIncidents, phones: rawPhones }) => {
    const { userLocation, layerVisibility } = useStore();
>>>>>>> Stashed changes
=======
export const Map: React.FC<MapProps> = ({ routes, selectedRouteId, setSelectedRouteId, incidents: rawIncidents, phones: rawPhones }) => {
    const { userLocation, layerVisibility } = useStore();
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        }, 30);
=======
        }, 15);
>>>>>>> Stashed changes
=======
        }, 15);
>>>>>>> Stashed changes

        return () => clearInterval(interval);
    }, [selectedRouteId, routes]);

    const center: [number, number] = userLocation
        ? [userLocation.latitude, userLocation.longitude]
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
        : [38.9404, -92.3277];

    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';

    // Simple Clustering logic for incidents
    const clusterMarkers = (items: Incident[]) => {
        if (!layerVisibility.incidents) return [];
        if (items.length <= 12) return items.map(item => ({ type: 'single', data: item }));

        // Very basic spatial clustering (0.001 deg ~ 100m)
        const clusters: { type: 'cluster' | 'single', data: any, count?: number }[] = [];
        const usedIndex = new Set();

        for (let i = 0; i < items.length; i++) {
            if (usedIndex.has(i)) continue;
            const cluster = [items[i]];
            usedIndex.add(i);

            for (let j = i + 1; j < items.length; j++) {
                if (usedIndex.has(j)) continue;
                const dist = Math.sqrt(
                    Math.pow(items[i].location.latitude - items[j].location.latitude, 2) +
                    Math.pow(items[i].location.longitude - items[j].location.longitude, 2)
                );
                if (dist < 0.002) {
                    cluster.push(items[j]);
                    usedIndex.add(j);
                }
            }

            if (cluster.length > 1) {
                clusters.push({ type: 'cluster', count: cluster.length, data: cluster[0].location });
            } else {
                clusters.push({ type: 'single', data: cluster[0] });
            }
        }
        return clusters;
    };

    const clusteredIncidents = clusterMarkers(rawIncidents);

    // Calculate distance markers for selected route
    const getDistanceMarkers = () => {
        if (!selectedRouteId || !layerVisibility.routes) return [];
        const selectedRoute = routes.find(r => r.route.id === selectedRouteId);
        if (!selectedRoute) return [];

        const points = selectedRoute.route.geometry.coordinates;
        const markers: { pos: [number, number], label: string }[] = [];
        let totalDist = 0;

        for (let i = 1; i < points.length; i++) {
            const p1 = L.latLng(points[i - 1][1], points[i - 1][0]);
            const p2 = L.latLng(points[i][1], points[i][0]);
            totalDist += p1.distanceTo(p2);

            // Add marker every ~400m (approx 0.25 mile)
            if (totalDist >= 400 && markers.length < 10) {
                const miles = (markers.length + 1) * 0.25;
                markers.push({
                    pos: [points[i][1], points[i][0]],
                    label: `${miles.toFixed(2)} mi`
                });
                totalDist = 0;
            }
        }
        return markers;
    };

    const distanceMarkers = getDistanceMarkers();

    return (
        <div className="map-container">
            <ConditionsBanner />
            <MapLegend />

            <MapContainer
                center={center as any}
                zoom={16}
                minZoom={14}
                maxZoom={19}
                scrollWheelZoom={true}
                zoomControl={false}
                preferCanvas={true}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; CARTO'
                    url={isDarkMode
                        ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
                        : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
                    }
                    maxZoom={19}
                    maxNativeZoom={19}
                />

                <ZoomControl />
                <LocateControl />
                <LayerControl />
                <FullscreenControl />

                {userLocation && (
                    <>
                        <Marker position={[userLocation.latitude, userLocation.longitude] as [number, number]}>
                            <Popup>You are here</Popup>
                        </Marker>
                        <Circle
                            center={[userLocation.latitude, userLocation.longitude] as [number, number]}
                            radius={40}
                            className="location-accuracy-circle"
                        />
                    </>
                )}

                {layerVisibility.routes && routes.map((rankedRoute) => {
                    const isSelected = rankedRoute.route.id === selectedRouteId;
                    const { color } = getSafetyDetails(rankedRoute.safety_analysis.risk_score);
                    const positions = rankedRoute.route.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);

                    return (
                        <React.Fragment key={rankedRoute.route.id}>
                            <Polyline
                                positions={positions}
                                eventHandlers={{ click: () => setSelectedRouteId(rankedRoute.route.id) }}
                                pathOptions={{
                                    color,
                                    weight: isSelected ? 8 : 6,
                                    opacity: isSelected ? 0.3 : 0.15,
                                    lineCap: 'round',
                                    lineJoin: 'round',
                                }}
                                className="route-polyline"
                            />
                            {isSelected && (
                                <Polyline
                                    positions={animatedPath}
                                    pathOptions={{ color, weight: 8, opacity: 1, lineCap: 'round', lineJoin: 'round' }}
                                    className="route-polyline--selected"
                                />
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                            )}
                        </React.Fragment>
                    );
                })}

<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
                {/* Distance Markers */}
                {distanceMarkers.map((dm, idx) => (
                    <Marker key={idx} position={dm.pos} icon={L.divIcon({
                        className: 'distance-label-container',
                        html: `<div>${dm.label}</div>`,
                        iconSize: [40, 20]
                    })} />
                ))}

                {/* Clustered Incidents */}
                {clusteredIncidents.map((node: any, idx) => (
                    node.type === 'cluster' ? (
                        <Marker key={`c-${idx}`} position={[node.data.latitude, node.data.longitude]} icon={createClusterIcon(node.count)} />
                    ) : (
                        <Marker
                            key={node.data.id}
                            position={[node.data.location.latitude, node.data.location.longitude]}
                            icon={createIncidentIcon() as any}
                        >
                            <Popup>
                                <div style={{ padding: '8px', minWidth: '200px' }}>
                                    <h4 style={{ margin: 0, color: 'var(--color-safety-100)' }}>⚠️ {node.data.type}</h4>
                                    <p style={{ margin: '8px 0', fontSize: '12px' }}>{node.data.description}</p>
                                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                                        Reported: {new Date(node.data.date).toLocaleDateString()}
                                    </div>
                                </div>
                            </Popup>
                        </Marker>
                    )
                ))}

                {/* Emergency Phones */}
                {layerVisibility.phones && rawPhones.map((phone, index) => (
                    <Marker
                        key={phone.id ?? `phone-${index}`}
                        position={[phone.location.latitude, phone.location.longitude] as [number, number]}
                        icon={createEmergencyPhoneIcon() as any}
                    >
                        <Popup>
                            <div style={{ padding: '8px' }}>
                                <h4 style={{ margin: 0, color: 'var(--color-brand-blue)' }}>📞 Emergency Phone</h4>
                                <p style={{ margin: '8px 0', fontSize: '12px' }}>
                                    {phone.name ? `${phone.name} • ` : ''}Direct line to Security Dispatch.
                                </p>
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import { useStore } from '../../hooks/useStore';
import { createIncidentIcon, createEmergencyPhoneIcon, createClusterIcon, createUserLocationIcon } from './Markers';
import { getSafetyDetails } from '../../utils/formatters';
import type { RankedRoute } from '../../types/route';
import type { Incident, EmergencyPhone } from '../../types/incident';
import { MapLegend } from './MapLegend';
import { ConditionsBanner } from './ConditionsBanner';
import { ZoomControl, LocateControl, FullscreenControl, LayerControl } from './MapControls';
import ShuttleLayer from './ShuttleLayer';
import RiskHeatmap from './RiskHeatmap';
import InfrastructureLayer from './InfrastructureLayer';
import TrafficSignalLayer from './TrafficSignalLayer';
import { TransitStopsLayer } from './TransitStopsLayer';
import type { TransitStop } from '../../types/transit';
import 'leaflet/dist/leaflet.css';
import './map.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface MapProps {
    routes: RankedRoute[];
    selectedRouteId: string | null;
    setSelectedRouteId: (id: string | null) => void;
    incidents: Incident[];
    phones: EmergencyPhone[];
}

export const Map: React.FC<MapProps> = ({ routes, selectedRouteId, setSelectedRouteId, incidents: rawIncidents, phones: rawPhones }) => {
    const { userLocation, layerVisibility, isDarkMode } = useStore();
    const [animatedPath, setAnimatedPath] = React.useState<[number, number][]>([]);
    const [transitStops, setTransitStops] = React.useState<TransitStop[]>([]);

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
        }, 15);

        return () => clearInterval(interval);
    }, [selectedRouteId, routes]);

    // Fetch transit stops when layer is visible
    useEffect(() => {
        console.log('[Transit] Layer visible:', layerVisibility.transitStops, 'Stops loaded:', transitStops.length);
        if (layerVisibility.transitStops && transitStops.length === 0) {
            const fetchTransitStops = async () => {
                try {
                    console.log('[Transit] Fetching routes from:', `${API_BASE}/api/transit/routes`);
                    // Fetch all routes and their stops
                    const routesResponse = await fetch(`${API_BASE}/api/transit/routes`);
                    const routesData = await routesResponse.json();
                    console.log('[Transit] Routes:', routesData);

                    const allStops: TransitStop[] = [];
                    for (const route of routesData.routes) {
                        const stopsResponse = await fetch(`${API_BASE}/api/transit/routes/${route.id}/stops`);
                        const stopsData = await stopsResponse.json();
                        console.log(`[Transit] Route ${route.route_name} stops:`, stopsData.stops?.length);

                        // Add stops with lat/lon (filter out null coordinates)
                        const validStops = stopsData.stops
                            .filter((stop: any) => stop.latitude != null && stop.longitude != null)
                            .map((stop: any) => ({
                                ...stop,
                                route_name: route.route_name,
                                route_color: route.route_color
                            }));

                        allStops.push(...validStops);
                    }

                    console.log('[Transit] Total valid stops:', allStops.length, allStops.slice(0, 2));
                    setTransitStops(allStops);
                } catch (error) {
                    console.error('[Transit] Error fetching transit stops:', error);
                }
            };

            fetchTransitStops();
        }
    }, [layerVisibility.transitStops, transitStops.length]);

    const center: [number, number] = userLocation
        ? [userLocation.latitude, userLocation.longitude]
        : [38.9404, -92.3277];



    // Simple Clustering logic for incidents
    type ClusterItem = { type: 'cluster'; count: number; data: { latitude: number; longitude: number } };
    type SingleItem = { type: 'single'; data: Incident };
    type MapItem = ClusterItem | SingleItem;

    const clusterMarkers = (items: Incident[]): MapItem[] => {
        if (!layerVisibility.incidents) return [];
        if (items.length <= 12) return items.map(item => ({ type: 'single', data: item } as SingleItem));

        const clusters: MapItem[] = [];
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
                        <Marker
                            position={[userLocation.latitude, userLocation.longitude] as [number, number]}
                            icon={createUserLocationIcon()}
                        >
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
                            )}
                        </React.Fragment>
                    );
                })}

                {/* Distance Markers */}
                {distanceMarkers.map((dm, idx) => (
                    <Marker key={idx} position={dm.pos} icon={L.divIcon({
                        className: 'distance-label-container',
                        html: `<div>${dm.label}</div>`,
                        iconSize: [40, 20]
                    })} />
                ))}

                {/* Crime/Incident Markers (clustered) */}
                {layerVisibility.incidents && clusteredIncidents.map((item, idx) => {
                    if (item.type === 'cluster') {
                        return (
                            <Marker
                                key={`cluster-${idx}`}
                                position={[item.data.latitude, item.data.longitude] as [number, number]}
                                icon={createClusterIcon(item.count)}
                            >
                                <Popup>
                                    <div style={{ fontSize: '12px' }}>
                                        <strong>{item.count} incidents</strong> reported in this area
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    }
                    const incident = item.data as Incident;
                    return (
                        <Marker
                            key={`incident-${incident.id}`}
                            position={[incident.location.latitude, incident.location.longitude] as [number, number]}
                            icon={createIncidentIcon()}
                        >
                            <Popup>
                                <div style={{ fontSize: '12px' }}>
                                    <strong>{incident.type}</strong>
                                    <br />
                                    {incident.description}
                                    <br />
                                    <span style={{ color: '#888' }}>{incident.date}</span>
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}

                {/* Emergency Phone Markers */}
                {layerVisibility.phones && rawPhones.map((phone, idx) => (
                    <Marker
                        key={`phone-${phone.id || idx}`}
                        position={[phone.location.latitude, phone.location.longitude] as [number, number]}
                        icon={createEmergencyPhoneIcon()}
                    >
                        <Popup>
                            <div style={{ fontSize: '12px' }}>
                                <strong>{phone.name || 'Emergency Phone'}</strong>
                            </div>
                        </Popup>
                    </Marker>
                ))}

                {/* Shuttle routes, stops, and live positions */}
                {layerVisibility.shuttles && <ShuttleLayer />}

                {/* Crime/incident risk heatmap */}
                {layerVisibility.heatmap && <RiskHeatmap />}

                {/* Safety infrastructure (crosswalks, lights) */}
                {layerVisibility.infrastructure && <InfrastructureLayer />}

                {/* Real traffic signal locations from OpenStreetMap */}
                {layerVisibility.trafficSignals && <TrafficSignalLayer />}

                {/* Transit stops with schedules */}
                {layerVisibility.transitStops && <TransitStopsLayer stops={transitStops} />}
            </MapContainer>
        </div>
    );
};

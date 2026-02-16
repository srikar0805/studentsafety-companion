import React, { useEffect } from 'react';
import { getSafetyDetails } from '../../utils/formatters';
import type { RankedRoute } from '../../types/route';
import type { Incident, EmergencyPhone } from '../../types/incident';
import { MapLegend } from './MapLegend';
import { ConditionsBanner } from './ConditionsBanner';
import { ZoomControl, LocateControl, FullscreenControl, LayerControl } from './MapControls';
import 'leaflet/dist/leaflet.css';
import './map.css';

interface MapProps {
    routes: RankedRoute[];
    selectedRouteId: string | null;
    setSelectedRouteId: (id: string | null) => void;
    incidents: Incident[];
    phones: EmergencyPhone[];
}

export const Map: React.FC<MapProps> = ({ routes, selectedRouteId, setSelectedRouteId, incidents: rawIncidents, phones: rawPhones }) => {
    const { userLocation, layerVisibility } = useStore();
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
        }, 15);

        return () => clearInterval(interval);
    }, [selectedRouteId, routes]);

    const center: [number, number] = userLocation
        ? [userLocation.latitude, userLocation.longitude]
                            )}
                        </React.Fragment>
                    );
                })}

                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

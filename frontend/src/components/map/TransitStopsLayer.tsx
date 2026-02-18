import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { TransitStop } from '../../types/transit';
import { TransitStopPopup } from './TransitStopPopup';


interface TransitStopsLayerProps {
    stops: TransitStop[];
}

export const TransitStopsLayer: React.FC<TransitStopsLayerProps> = ({ stops }) => {
    // Create dot icon with the route's color
    const createIcon = (color: string) => L.divIcon({
        html: `
      <div style="
        width: 10px;
        height: 10px;
        background-color: ${color || '#2563eb'};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>
    `,
        className: 'transit-stop-marker',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
        popupAnchor: [0, -7]
    });

    return (
        <>
            {stops.map(stop => (
                <Marker
                    key={`transit-${stop.id}`}
                    position={[stop.latitude, stop.longitude]}
                    icon={createIcon(stop.route_color || '#2563eb')}
                >
                    <Popup maxWidth={300} minWidth={240}>
                        <TransitStopPopup stop={stop} />
                    </Popup>
                </Marker>
            ))}
        </>
    );
};

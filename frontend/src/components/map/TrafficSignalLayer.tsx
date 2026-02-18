import { useEffect, useState, useMemo } from 'react';
import { Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface TrafficSignal {
    id: number;
    lat: number;
    lon: number;
    name: string;
}

function createSignalIcon(zoom: number) {
    // Scale icon based on zoom: tiny at zoom 14, normal at zoom 18+
    if (zoom <= 14) {
        return L.divIcon({
            className: 'traffic-signal-icon',
            html: `<div style="width:6px;height:6px;background:#f59e0b;border-radius:50%;opacity:0.5;"></div>`,
            iconSize: [6, 6],
            iconAnchor: [3, 3],
        });
    }
    if (zoom <= 15) {
        return L.divIcon({
            className: 'traffic-signal-icon',
            html: `<div style="width:8px;height:8px;background:#f59e0b;border-radius:50%;border:1px solid white;opacity:0.6;"></div>`,
            iconSize: [8, 8],
            iconAnchor: [4, 4],
        });
    }
    if (zoom <= 16) {
        return L.divIcon({
            className: 'traffic-signal-icon',
            html: `<div style="width:12px;height:12px;background:#f59e0b;border-radius:50%;border:1px solid white;opacity:0.75;"></div>`,
            iconSize: [12, 12],
            iconAnchor: [6, 6],
        });
    }
    if (zoom <= 17) {
        return L.divIcon({
            className: 'traffic-signal-icon',
            html: `<div style="font-size:12px;width:18px;height:18px;display:flex;align-items:center;justify-content:center;background:rgba(245,158,11,0.85);border-radius:50%;border:1.5px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.2);">🚦</div>`,
            iconSize: [18, 18],
            iconAnchor: [9, 9],
        });
    }
    // zoom >= 18: full size
    return L.divIcon({
        className: 'traffic-signal-icon',
        html: `<div style="font-size:14px;width:22px;height:22px;display:flex;align-items:center;justify-content:center;background:rgba(245,158,11,0.85);border-radius:50%;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3);">🚦</div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
    });
}

export default function TrafficSignalLayer() {
    const [signals, setSignals] = useState<TrafficSignal[]>([]);
    const map = useMap();
    const [zoom, setZoom] = useState(map.getZoom());

    useMapEvents({
        zoomend: () => setZoom(map.getZoom()),
    });

    useEffect(() => {
        fetch(`${API_BASE}/api/traffic-signals`)
            .then(r => r.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setSignals(data);
                }
            })
            .catch(err => console.error('Failed to fetch traffic signals:', err));
    }, []);

    const icon = useMemo(() => createSignalIcon(zoom), [zoom]);

    return (
        <>
            {signals.map((signal) => (
                <Marker
                    key={`signal-${signal.id}`}
                    position={[signal.lat, signal.lon]}
                    icon={icon}
                >
                    <Popup>
                        <div style={{ fontSize: '12px' }}>
                            <strong>Traffic Signal</strong>
                            <br />
                            {signal.name}
                        </div>
                    </Popup>
                </Marker>
            ))}
        </>
    );
}

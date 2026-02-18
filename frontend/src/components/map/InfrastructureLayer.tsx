import { useEffect, useState } from 'react';
import { CircleMarker, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface InfraFeature {
    type: string;
    lat: number;
    lon: number;
    properties: { name?: string; radius?: number };
}

const typeConfig: Record<string, { icon: string; color: string; label: string }> = {
    traffic_signal: { icon: '🚦', color: '#f59e0b', label: 'Traffic Signal' },
    crosswalk: { icon: '🚶', color: '#3b82f6', label: 'Crosswalk' },
    streetlight_zone: { icon: '💡', color: '#fbbf24', label: 'Lit Area' },
};

function createInfraIcon(emoji: string) {
    return L.divIcon({
        className: 'infra-icon',
        html: `<div style="
      font-size: 16px;
      width: 24px; height: 24px;
      display: flex; align-items: center; justify-content: center;
      background: rgba(15, 23, 42, 0.7);
      border-radius: 50%;
      border: 1px solid rgba(255,255,255,0.15);
    ">${emoji}</div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
    });
}

export default function InfrastructureLayer() {
    const [features, setFeatures] = useState<InfraFeature[]>([]);

    useEffect(() => {
        fetch(`${API_BASE}/api/infrastructure`)
            .then(r => r.json())
            .then(setFeatures)
            .catch(err => console.error('Failed to fetch infrastructure:', err));
    }, []);

    return (
        <>
            {features.map((f, idx) => {
                const config = typeConfig[f.type] || typeConfig.traffic_signal;

                if (f.type === 'streetlight_zone') {
                    return (
                        <CircleMarker
                            key={`infra-${idx}`}
                            center={[f.lat, f.lon]}
                            radius={f.properties.radius ? f.properties.radius / 3 : 25}
                            pathOptions={{
                                color: 'transparent',
                                fillColor: config.color,
                                fillOpacity: 0.12,
                            }}
                        >
                            <Popup>
                                <div style={{ fontSize: '12px' }}>
                                    <strong>{config.icon} {f.properties.name || config.label}</strong>
                                </div>
                            </Popup>
                        </CircleMarker>
                    );
                }

                return (
                    <Marker
                        key={`infra-${idx}`}
                        position={[f.lat, f.lon]}
                        icon={createInfraIcon(config.icon)}
                    >
                        <Popup>
                            <div style={{ fontSize: '12px' }}>
                                <strong>{config.icon} {f.properties.name || config.label}</strong>
                            </div>
                        </Popup>
                    </Marker>
                );
            })}
        </>
    );
}

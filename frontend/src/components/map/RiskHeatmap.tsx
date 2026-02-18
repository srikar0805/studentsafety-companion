import { useEffect, useState } from 'react';
import { CircleMarker, Popup } from 'react-leaflet';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface RiskCell {
    geometry: { coordinates: [number, number] };
    properties: { risk_score: number; incident_count: number };
}

function getRiskColor(score: number): string {
    if (score > 0.7) return '#ef4444';
    if (score > 0.5) return '#f97316';
    if (score > 0.3) return '#eab308';
    return '#22c55e';
}

export default function RiskHeatmap() {
    const [cells, setCells] = useState<RiskCell[]>([]);

    useEffect(() => {
        const hour = new Date().getHours();
        fetch(`${API_BASE}/api/risk-zones?time=${hour}`)
            .then(r => r.json())
            .then(data => setCells(data.features || []))
            .catch(err => console.error('Failed to fetch risk zones:', err));
    }, []);

    return (
        <>
            {cells.map((cell, idx) => {
                const [lon, lat] = cell.geometry.coordinates;
                const score = cell.properties.risk_score;
                return (
                    <CircleMarker
                        key={`risk-${idx}`}
                        center={[lat, lon]}
                        radius={score > 0.5 ? 30 : 20}
                        pathOptions={{
                            color: 'transparent',
                            fillColor: getRiskColor(score),
                            fillOpacity: 0.15 + score * 0.35,
                        }}
                    >
                        <Popup>
                            <div style={{ fontSize: '12px' }}>
                                <strong>Risk Score: {(score * 100).toFixed(0)}%</strong>
                                <br />
                                Incidents nearby: {cell.properties.incident_count}
                            </div>
                        </Popup>
                    </CircleMarker>
                );
            })}
        </>
    );
}

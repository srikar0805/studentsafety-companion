import L from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';
import { AlertCircle, Phone } from 'lucide-react';

export const createIncidentIcon = () => {
    const iconHtml = renderToStaticMarkup(
        <div className="marker-incident--pulse" style={{
            backgroundColor: 'var(--color-safety-100)',
            color: 'white',
            borderRadius: '50%',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
        </div>
    );

    return L.divIcon({
        html: iconHtml,
        className: 'custom-marker',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
    });
};

export const createEmergencyPhoneIcon = () => {
    const iconHtml = renderToStaticMarkup(
        <div style={{
            backgroundColor: 'var(--color-brand-blue)',
            color: 'white',
            borderRadius: '50%',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '2px solid white',
        </div>
    );

    return L.divIcon({
        html: iconHtml,
};

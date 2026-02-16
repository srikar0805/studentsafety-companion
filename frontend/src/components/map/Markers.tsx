import L from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';
import { AlertCircle, Phone } from 'lucide-react';

export const createIncidentIcon = () => {
    const iconHtml = renderToStaticMarkup(
<<<<<<< Updated upstream
        <div style={{
=======
        <div className="marker-incident--pulse" style={{
>>>>>>> Stashed changes
            backgroundColor: 'var(--color-safety-100)',
            color: 'white',
            borderRadius: '50%',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
<<<<<<< Updated upstream
            border: '2px solid white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
        }}>
            <AlertCircle size={18} />
=======
            border: '3px solid white',
            boxShadow: '0 2px 8px rgba(239, 68, 68, 0.4)'
        }}>
            <AlertCircle size={20} fill="rgba(255,255,255,0.2)" />
>>>>>>> Stashed changes
        </div>
    );

    return L.divIcon({
        html: iconHtml,
<<<<<<< Updated upstream
        className: '',
=======
        className: 'custom-marker',
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            boxShadow: '0 0 10px var(--color-brand-blue)',
        }}>
            <Phone size={18} />
=======
            boxShadow: '0 2px 4px rgba(37, 99, 235, 0.3)',
            outline: '2px solid rgba(16, 185, 129, 0.4)'
        }}>
            <Phone size={18} fill="currentColor" />
>>>>>>> Stashed changes
        </div>
    );

    return L.divIcon({
        html: iconHtml,
<<<<<<< Updated upstream
        className: '',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
    });
=======
        className: 'custom-marker',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
    });
}; export const createClusterIcon = (count: number) => {
    return L.divIcon({
        html: `<div class="marker-cluster">${count}</div>`,
        className: 'custom-cluster-marker',
        iconSize: [36, 36],
        iconAnchor: [18, 18],
    });
>>>>>>> Stashed changes
};

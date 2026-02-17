import React, { useState } from 'react';
import { useMap } from 'react-leaflet';
import { Plus, Minus, Crosshair, Maximize, Minimize, Layers, Check } from 'lucide-react';
import { useStore } from '../../hooks/useStore';
import L from 'leaflet';

const stopPropagation = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
};

const preventMapInteraction = {
    onClick: stopPropagation,
    onMouseDown: stopPropagation,
    onDoubleClick: stopPropagation,
    onScroll: (e: any) => e.stopPropagation(),
};

export const ZoomControl: React.FC = () => {
    const map = useMap();

    return (
        <div className="leaflet-top leaflet-right" style={{ marginTop: '120px' }}>
            <div className="leaflet-control map-custom-control" {...preventMapInteraction}>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={(e) => { stopPropagation(e); map.zoomIn(); }}
                    title="Zoom In"
                >
                    <Plus size={20} />
                </button>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={(e) => { stopPropagation(e); map.zoomOut(); }}
                    title="Zoom Out"
                >
                    <Minus size={20} />
                </button>
            </div>
        </div>
    );
};

import { useResponsive } from '../../hooks/useResponsive';

export const LocateControl: React.FC = () => {
    const map = useMap();
    const setUserLocation = useStore((state) => state.setUserLocation);
    const { isDesktop } = useResponsive();

    React.useEffect(() => {
        // Handler for geolocation found
        const onLocationFound = (e: any) => {
            if (e && e.latlng) {
                setUserLocation({ latitude: e.latlng.lat, longitude: e.latlng.lng });

                // Apply offset if on desktop to avoid being covered by chat
                let targetLng = e.latlng.lng;
                if (isDesktop) {
                    // Shift center by half of chat width + margin (420px + 24px) / 2 = 222px
                    // This puts the pin perfectly in the center of the remaining space to the right
                    const point = map.project(e.latlng, 18);
                    const newPoint = point.subtract([222, 0]);
                    const newCenter = map.unproject(newPoint, 18);
                    map.setView(newCenter, 18);
                } else {
                    map.setView(e.latlng, 18);
                }
            }
        };
        map.on('locationfound', onLocationFound);

        // Trigger initial location without auto-setView, let the handler do it
        map.locate({ setView: false, maxZoom: 18 });

        return () => {
            map.off('locationfound', onLocationFound);
        };
    }, [map, setUserLocation, isDesktop]);

    const handleLocate = (e: React.MouseEvent) => {
        stopPropagation(e);
        map.locate({ setView: false, maxZoom: 18 });
    };

    return (
        <div className="leaflet-top leaflet-right" style={{ marginTop: '230px' }}>
            <div className="leaflet-control map-custom-control" {...preventMapInteraction}>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={handleLocate}
                    title="Locate Me"
                >
                    <Crosshair size={20} />
                </button>
            </div>
        </div>
    );
};

export const LayerControl: React.FC = () => {
    const { layerVisibility, toggleLayer } = useStore();
    const [isOpen, setIsOpen] = useState(false);

    const layers = [
        { id: 'routes', label: 'Safety Routes', icon: '🛣️' },
        { id: 'incidents', label: 'Recent Incidents', icon: '⚠️' },
        { id: 'phones', label: 'Emergency Phones', icon: '📞' },
        { id: 'patrolZones', label: 'Patrol Zones', icon: '🛡️' },
    ] as const;

    return (
        <div className="leaflet-top leaflet-right" style={{ marginTop: '300px' }}>
            <div className="leaflet-control map-custom-control" style={{ position: 'relative' }} {...preventMapInteraction}>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={(e) => { stopPropagation(e); setIsOpen(!isOpen); }}
                    title="Layer Controls"
                >
                    <Layers size={20} />
                </button>

                {isOpen && (
                    <div style={{
                        position: 'absolute',
                        right: '54px',
                        top: '0',
                        backgroundColor: 'var(--color-bg-card)',
                        border: '1px solid var(--color-border-subtle)',
                        borderRadius: '12px',
                        padding: '12px',
                        minWidth: '200px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        zIndex: 1001,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '4px'
                    }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: '8px', padding: '0 4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Map Overlays
                        </div>
                        {layers.map((layer) => (
                            <button
                                key={layer.id}
                                onClick={(e) => { stopPropagation(e); toggleLayer(layer.id); }}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    padding: '10px 12px',
                                    borderRadius: '8px',
                                    backgroundColor: layerVisibility[layer.id] ? 'var(--color-brand-blue-light)' : 'transparent',
                                    color: layerVisibility[layer.id] ? 'var(--color-brand-blue)' : 'var(--color-text-primary)',
                                    border: 'none',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    width: '100%',
                                    textAlign: 'left',
                                    fontSize: '13px',
                                    fontWeight: 500
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <span>{layer.icon}</span>
                                    <span>{layer.label}</span>
                                </div>
                                {layerVisibility[layer.id] && <Check size={14} />}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export const FullscreenControl: React.FC = () => {
    const [isFullscreen, setIsFullscreen] = React.useState(false);

    const toggleFullscreen = (e: React.MouseEvent) => {
        stopPropagation(e);
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            setIsFullscreen(true);
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
                setIsFullscreen(false);
            }
        }
    };

    return (
        <div className="leaflet-top leaflet-right" style={{ marginTop: '370px' }}>
            <div className="leaflet-control map-custom-control" {...preventMapInteraction}>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={toggleFullscreen}
                    title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
                >
                    {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
                </button>
            </div>
        </div>
    );
};


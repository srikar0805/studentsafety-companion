import React, { useState } from 'react';
import { useMap } from 'react-leaflet';
import { Plus, Minus, Crosshair, Maximize, Minimize, Layers, Check } from 'lucide-react';
import { useStore } from '../../hooks/useStore';

export const ZoomControl: React.FC = () => {
    const map = useMap();

    return (
        <div className="leaflet-top leaflet-right">
            <div className="leaflet-control map-custom-control">
                <button
                    className="map-control-btn touch-optimized"
                    onClick={() => map.zoomIn()}
                    title="Zoom In"
                >
                    <Plus size={20} />
                </button>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={() => map.zoomOut()}
                    title="Zoom Out"
                >
                    <Minus size={20} />
                </button>
            </div>
        </div>
    );
};

export const LocateControl: React.FC = () => {
    const map = useMap();

    const handleLocate = () => {
        map.setZoom(17);
        map.locate({ setView: true, maxZoom: 18 });
    };

    return (
        <div className="leaflet-top leaflet-right" style={{ marginTop: '106px' }}>
            <div className="leaflet-control map-custom-control">
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
        <div className="leaflet-top leaflet-right" style={{ marginTop: '162px' }}>
            <div className="leaflet-control map-custom-control" style={{ position: 'relative' }}>
                <button
                    className="map-control-btn touch-optimized"
                    onClick={() => setIsOpen(!isOpen)}
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
                                onClick={() => toggleLayer(layer.id)}
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

    const toggleFullscreen = () => {
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
        <div className="leaflet-top leaflet-right" style={{ marginTop: '218px' }}>
            <div className="leaflet-control map-custom-control">
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

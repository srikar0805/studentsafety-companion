import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Map as MapIcon, AlertCircle, Phone, Shield } from 'lucide-react';

export const MapLegend: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            zIndex: 1000,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            width: isCollapsed ? '48px' : '250px',
            height: isCollapsed ? '48px' : 'auto',
            overflow: 'hidden',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontFamily: "'Outfit', sans-serif"
        }}>
            <div
                onClick={() => setIsCollapsed(!isCollapsed)}
                style={{
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    backgroundColor: 'transparent'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700, fontSize: '13px', letterSpacing: '0.02em', color: 'var(--color-text-primary)' }}>
                    <MapIcon size={18} className="text-brand-blue" />
                    {!isCollapsed && "SAFETY LEGEND"}
                </div>
                {!isCollapsed && (isCollapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />)}
            </div>

            {!isCollapsed && (
                <div style={{ padding: '0 16px 16px 16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    <hr style={{ border: 'none', borderTop: '1px solid var(--color-border-subtle)', margin: '0 0 4px 0' }} />

                    {/* Route Safety Scale */}
                    <div>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Routes
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {[
                                { color: '#10b981', label: 'Very Safe (0-20)' },
                                { color: '#84cc16', label: 'Safe (21-40)' },
                                { color: '#f59e0b', label: 'Moderate (41-60)' },
                                { color: '#f97316', label: 'Caution (61-80)' },
                                { color: '#ef4444', label: 'Warning (81-100)' },
                            ].map((item) => (
                                <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <div style={{ width: '24px', height: '4px', borderRadius: '2px', backgroundColor: item.color }} />
                                    <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: '14px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Markers
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <div style={{ color: '#ef4444' }}><AlertCircle size={14} fill="rgba(239, 68, 68, 0.1)" /></div>
                                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Recent Incident</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <div style={{ color: '#2563eb' }}><Phone size={14} fill="rgba(37, 99, 235, 0.1)" /></div>
                                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Emergency Phone</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <div style={{ color: '#2563eb', opacity: 0.6 }}><Shield size={14} /></div>
                                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>High Patrol Area</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

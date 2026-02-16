import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info, AlertCircle, Phone, Shield } from 'lucide-react';

export const MapLegend: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div style={{
            position: 'absolute',
            bottom: '24px',
            left: '24px',
            zIndex: 1000,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(8px)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-lg)',
            width: isCollapsed ? 'auto' : '220px',
            overflow: 'hidden',
            transition: 'all 0.3s ease'
        }}>
            <div
                onClick={() => setIsCollapsed(!isCollapsed)}
                style={{
                    padding: '10px 14px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    borderBottom: isCollapsed ? 'none' : '1px solid var(--color-gray-100)',
                    backgroundColor: 'var(--color-gray-50)'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '12px' }}>
                    <Info size={14} />
                    {!isCollapsed && "MAP LEGEND"}
                </div>
                {isCollapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>

            {!isCollapsed && (
                <div style={{ padding: '14px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {/* Route Safety Scale */}
                    <div>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-gray-500)', marginBottom: '8px' }}>
                            SAFETY LEVEL
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                            {[
                                { color: 'var(--color-safety-0)', label: 'Very Safe (0-20)' },
                                { color: 'var(--color-safety-40)', label: 'Safe (21-40)' },
                                { color: 'var(--color-safety-60)', label: 'Moderate (41-60)' },
                                { color: 'var(--color-safety-80)', label: 'Caution (61-80)' },
                                { color: 'var(--color-safety-100)', label: 'Avoid (81-100)' },
                            ].map((item) => (
                                <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <div style={{ width: '12px', height: '12px', borderRadius: '2px', backgroundColor: item.color }} />
                                    <span style={{ fontSize: '11px', color: 'var(--color-gray-700)' }}>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div style={{ borderTop: '1px solid var(--color-gray-100)', paddingTop: '10px' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div style={{ color: 'var(--color-safety-100)' }}><AlertCircle size={14} /></div>
                                <span style={{ fontSize: '11px', color: 'var(--color-gray-700)' }}>Recent Incident</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div style={{ color: 'var(--color-brand-blue)' }}><Phone size={14} /></div>
                                <span style={{ fontSize: '11px', color: 'var(--color-gray-700)' }}>Emergency Phone</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div style={{ color: 'var(--color-brand-blue)' }}><Shield size={14} /></div>
                                <span style={{ fontSize: '11px', color: 'var(--color-gray-700)' }}>High Patrol Area</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

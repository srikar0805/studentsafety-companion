import React, { useState } from 'react';
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
import { ChevronDown, ChevronUp, Info, AlertCircle, Phone, Shield } from 'lucide-react';
=======
import { ChevronDown, ChevronUp, Map as MapIcon, AlertCircle, Phone, Shield } from 'lucide-react';
>>>>>>> Stashed changes
=======
import { ChevronDown, ChevronUp, Map as MapIcon, AlertCircle, Phone, Shield } from 'lucide-react';
>>>>>>> Stashed changes
=======
import { ChevronDown, ChevronUp, Map as MapIcon, AlertCircle, Phone, Shield } from 'lucide-react';
>>>>>>> Stashed changes
=======
import { ChevronDown, ChevronUp, Map as MapIcon, AlertCircle, Phone, Shield } from 'lucide-react';
>>>>>>> Stashed changes

export const MapLegend: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div style={{
            position: 'absolute',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        }}>
            <div
                onClick={() => setIsCollapsed(!isCollapsed)}
                style={{
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                    padding: '10px 14px',
=======
                    padding: '12px 16px',
>>>>>>> Stashed changes
=======
                    padding: '12px 16px',
>>>>>>> Stashed changes
=======
                    padding: '12px 16px',
>>>>>>> Stashed changes
=======
                    padding: '12px 16px',
>>>>>>> Stashed changes
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                                </div>
                            ))}
                        </div>
                    </div>

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

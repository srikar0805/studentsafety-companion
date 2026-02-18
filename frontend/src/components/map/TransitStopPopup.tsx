import React, { useState, useEffect } from 'react';
import type { TransitStop, NextBusInfo, ScheduleEntry } from '../../types/transit';
import { calculateNextBus, formatTime12Hour } from '../../utils/transitTime';
import { Bus, MapPin } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface TransitStopPopupProps {
    stop: TransitStop;
}

export const TransitStopPopup: React.FC<TransitStopPopupProps> = ({ stop }) => {
    const [nextBus, setNextBus] = useState<NextBusInfo | null>(null);
    const [loading, setLoading] = useState(true);
    const [routeColor, setRouteColor] = useState<string>('#2563eb');

    useEffect(() => {
        // Fetch schedule for this stop's route
        const fetchSchedule = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/transit/routes/${stop.route_id}/schedule`);
                const data = await response.json();

                // Filter schedules for this specific stop
                const stopSchedules: ScheduleEntry[] = data.schedule.filter(
                    (s: ScheduleEntry) => s.stop_id === stop.id
                );

                const nextBusInfo = calculateNextBus(stopSchedules, new Date());
                setNextBus(nextBusInfo);

                // Get route color
                const routeResponse = await fetch(`${API_BASE}/api/transit/routes/${stop.route_id}`);
                const routeData = await routeResponse.json();
                setRouteColor(routeData.route_color || '#2563eb');

                setLoading(false);
            } catch (error) {
                console.error('Error fetching transit schedule:', error);
                setLoading(false);
            }
        };

        fetchSchedule();
    }, [stop]);

    return (
        <div style={{
            minWidth: '240px',
            padding: '12px',
            fontFamily: "'Outfit', sans-serif"
        }}>
            {/* Route and Stop Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '8px',
                paddingBottom: '8px',
                borderBottom: '1px solid rgba(0,0,0,0.1)'
            }}>
                <div style={{
                    width: '6px',
                    height: '32px',
                    borderRadius: '3px',
                    backgroundColor: routeColor
                }} />
                <div style={{ flex: 1 }}>
                    <div style={{
                        fontWeight: 700,
                        fontSize: '13px',
                        color: routeColor,
                        textTransform: 'uppercase',
                        letterSpacing: '0.03em'
                    }}>
                        {stop.route_name || `Route #${stop.route_id}`}
                    </div>
                    <div style={{
                        fontSize: '11px',
                        color: '#666',
                        marginTop: '2px'
                    }}>
                        Stop {stop.stop_code}
                    </div>
                </div>
            </div>

            {/* Stop Name */}
            <div style={{
                display: 'flex',
                alignItems: 'start',
                gap: '6px',
                marginBottom: '12px'
            }}>
                <MapPin size={14} color="#888" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div style={{
                    fontSize: '13px',
                    color: '#333',
                    fontWeight: 500,
                    lineHeight: '1.4'
                }}>
                    {stop.stop_name}
                </div>
            </div>

            {/* Next Bus Info */}
            {loading ? (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px',
                    backgroundColor: '#f7f7f7',
                    borderRadius: '8px'
                }}>
                    <div style={{ fontSize: '12px', color: '#888' }}>Loading schedule...</div>
                </div>
            ) : nextBus?.next_arrival ? (
                <>
                    {/* Next Arrival */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '10px 12px',
                        backgroundColor: '#f0f9ff',
                        borderRadius: '8px',
                        marginBottom: '8px',
                        border: '1px solid #bfdbfe'
                    }}>
                        <Bus size={20} color={routeColor} />
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                Next Bus
                            </div>
                            <div style={{
                                display: 'flex',
                                alignItems: 'baseline',
                                gap: '8px',
                                marginTop: '2px'
                            }}>
                                <div style={{ fontSize: '18px', fontWeight: 700, color: routeColor }}>
                                    {formatTime12Hour(nextBus.next_arrival)}
                                </div>
                                <div style={{ fontSize: '13px', color: '#64748b', fontWeight: 600 }}>
                                    ({nextBus.minutes_until} min)
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Upcoming Times */}
                    {nextBus.upcoming_times.length > 1 && (
                        <div style={{
                            padding: '8px 12px',
                            backgroundColor: '#f7f7f7',
                            borderRadius: '6px'
                        }}>
                            <div style={{
                                fontSize: '10px',
                                color: '#888',
                                fontWeight: 600,
                                marginBottom: '6px',
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em'
                            }}>
                                Upcoming
                            </div>
                            <div style={{
                                display: 'flex',
                                flexWrap: 'wrap',
                                gap: '6px'
                            }}>
                                {nextBus.upcoming_times.slice(1, 4).map((time, idx) => (
                                    <span key={idx} style={{
                                        fontSize: '11px',
                                        color: '#555',
                                        fontWeight: 600,
                                        padding: '3px 8px',
                                        backgroundColor: 'white',
                                        borderRadius: '4px',
                                        border: '1px solid #e0e0e0'
                                    }}>
                                        {formatTime12Hour(time)}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            ) : (
                <div style={{
                    padding: '12px',
                    backgroundColor: '#fef2f2',
                    borderRadius: '8px',
                    border: '1px solid #fecaca',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '12px', color: '#991b1b', fontWeight: 600 }}>
                        No more buses today
                    </div>
                </div>
            )}
        </div>
    );
};

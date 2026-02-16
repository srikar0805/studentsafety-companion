import React, { useState, useEffect } from 'react';
import { Moon, Sun, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';

export const ConditionsBanner: React.FC = () => {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 60000);
        return () => clearInterval(timer);
    }, []);

    const hour = time.getHours();
    const isNight = hour >= 22 || hour < 6;

    return (
        <div style={{
            position: 'absolute',
            top: '24px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '10px 24px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: isNight ? 'var(--color-brand-blue-dark)' : 'var(--color-brand-blue-light)',
            color: isNight ? 'white' : 'var(--color-brand-blue)',
            boxShadow: 'var(--shadow-lg)',
            border: `1.5px solid ${isNight ? 'rgba(255,255,255,0.1)' : 'var(--color-brand-blue)'}`,
            backdropFilter: 'blur(8px)',
            whiteSpace: 'nowrap'
        }}>
            {isNight ? <Moon size={20} fill="currentColor" /> : <Sun size={20} fill="currentColor" />}

            <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '12px', fontWeight: 800, letterSpacing: '0.05em' }}>
                    {isNight ? 'NIGHTTIME CONDITIONS' : 'DAYTIME CONDITIONS'} ({format(time, 'h:mm a')})
                </span>
                <span style={{ fontSize: '10px', opacity: 0.8, fontWeight: 500 }}>
                    {isNight ? 'Risk levels adjusted for after-dark travel' : 'Standard safety protocols in effect'}
                </span>
            </div>

            {isNight && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginLeft: '8px',
                    padding: '2px 10px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: 'var(--color-safety-80)',
                    color: 'white',
                    fontSize: '10px',
                    fontWeight: 700
                }}>
                    <AlertTriangle size={12} />
                    CAUTION ADVISED
                </div>
            )}
        </div>
    );
};

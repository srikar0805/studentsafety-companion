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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    const isNight = hour >= 22 || hour < 6;

    return (
        <div style={{
            position: 'absolute',
            top: '24px',
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    const isNight = hour >= 21 || hour < 6; // Adjusted to match agent criteria (9pm+)

    return (
        <div className={isNight ? "conditions-banner--night" : ""} style={{
            position: 'absolute',
            top: '20px',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            padding: '10px 24px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: isNight ? 'var(--color-brand-blue-dark)' : 'var(--color-brand-blue-light)',
            color: isNight ? 'white' : 'var(--color-brand-blue)',
            boxShadow: 'var(--shadow-lg)',
            border: `1.5px solid ${isNight ? 'rgba(255,255,255,0.1)' : 'var(--color-brand-blue)'}`,
            backdropFilter: 'blur(8px)',
            whiteSpace: 'nowrap'
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            padding: '12px 24px',
            borderRadius: '24px',
            backgroundColor: isNight ? 'rgba(88, 28, 135, 0.95)' : 'rgba(37, 99, 235, 0.95)',
            color: 'white',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            backdropFilter: 'blur(10px)',
            whiteSpace: 'nowrap',
            transition: 'all 0.5s ease',
            fontFamily: "'Outfit', sans-serif"
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        }}>
            {isNight ? <Moon size={20} fill="currentColor" /> : <Sun size={20} fill="currentColor" />}

            <div style={{ display: 'flex', flexDirection: 'column' }}>
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                <span style={{ fontSize: '12px', fontWeight: 800, letterSpacing: '0.05em' }}>
                    {isNight ? 'NIGHTTIME CONDITIONS' : 'DAYTIME CONDITIONS'} ({format(time, 'h:mm a')})
                </span>
                <span style={{ fontSize: '10px', opacity: 0.8, fontWeight: 500 }}>
                    {isNight ? 'Risk levels adjusted for after-dark travel' : 'Standard safety protocols in effect'}
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                <span style={{ fontSize: '13px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                    {isNight ? 'NIGHTTIME CONDITIONS' : 'DAYTIME CONDITIONS'} ({format(time, 'h:mm a')})
                </span>
                <span style={{ fontSize: '11px', opacity: 0.9, fontWeight: 500 }}>
                    {isNight ? 'Higher risk - safety prioritized' : 'Risk levels are lower during daylight'}
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                </span>
            </div>

            {isNight && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginLeft: '8px',
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                    padding: '2px 10px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: 'var(--color-safety-80)',
                    color: 'white',
                    fontSize: '10px',
                    fontWeight: 700
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                    padding: '4px 12px',
                    borderRadius: '20px',
                    backgroundColor: 'rgba(239, 68, 68, 0.9)',
                    color: 'white',
                    fontSize: '10px',
                    fontWeight: 800,
                    letterSpacing: '0.02em'
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                }}>
                    <AlertTriangle size={12} />
                    CAUTION ADVISED
                </div>
            )}
        </div>
    );
};

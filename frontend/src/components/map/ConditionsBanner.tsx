import React, { useState, useEffect } from 'react';
import { Moon, Sun, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { useResponsive } from '../../hooks/useResponsive';

export const ConditionsBanner: React.FC = () => {
    const [time, setTime] = useState(new Date());
    const { isMobile } = useResponsive();

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 60000);
        return () => clearInterval(timer);
    }, []);

    const hour = time.getHours();
    const isNight = hour >= 21 || hour < 6; // Adjusted to match agent criteria (9pm+)

    return (
        <div className={isNight ? "conditions-banner--night" : ""} style={{
            position: 'absolute',
            top: isMobile ? '12px' : '88px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: isMobile ? '8px' : '12px',
            padding: isMobile ? '8px 16px' : '12px 24px',
            borderRadius: '24px',
            backgroundColor: isNight ? 'rgba(88, 28, 135, 0.95)' : 'rgba(37, 99, 235, 0.95)',
            color: 'white',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            backdropFilter: 'blur(10px)',
            whiteSpace: isMobile ? 'normal' : 'nowrap',
            transition: 'all 0.5s ease',
            fontFamily: "'Outfit', sans-serif",
            width: isMobile ? '90%' : 'auto',
            maxWidth: '100%',
            justifyContent: isMobile ? 'center' : 'flex-start',
            flexDirection: isMobile ? 'column' : 'row',
            textAlign: isMobile ? 'center' : 'left'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {isNight ? <Moon size={isMobile ? 16 : 20} fill="currentColor" /> : <Sun size={isMobile ? 16 : 20} fill="currentColor" />}

                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: isMobile ? '12px' : '13px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                        {isNight ? 'NIGHTTIME CONDITIONS' : 'DAYTIME CONDITIONS'} ({format(time, 'h:mm a')})
                    </span>
                    <span style={{ fontSize: isMobile ? '10px' : '11px', opacity: 0.9, fontWeight: 500 }}>
                        {isNight ? 'Higher risk - safety prioritized' : 'Risk levels are lower during daylight'}
                    </span>
                </div>
            </div>

            {isNight && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginLeft: isMobile ? 0 : '8px',
                    marginTop: isMobile ? '4px' : 0,
                    padding: '4px 12px',
                    borderRadius: '20px',
                    backgroundColor: 'rgba(239, 68, 68, 0.9)',
                    color: 'white',
                    fontSize: '10px',
                    fontWeight: 800,
                    letterSpacing: '0.02em',
                    width: isMobile ? '100%' : 'auto',
                    justifyContent: 'center'
                }}>
                    <AlertTriangle size={12} />
                    CAUTION ADVISED
                </div>
            )}
        </div>
    );
};

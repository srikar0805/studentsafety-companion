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
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
        }}>
            {isNight ? <Moon size={20} fill="currentColor" /> : <Sun size={20} fill="currentColor" />}

            <div style={{ display: 'flex', flexDirection: 'column' }}>
                </span>
            </div>

            {isNight && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginLeft: '8px',
                }}>
                    <AlertTriangle size={12} />
                    CAUTION ADVISED
                </div>
            )}
        </div>
    );
};

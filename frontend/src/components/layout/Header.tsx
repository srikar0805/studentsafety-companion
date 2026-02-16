import React from 'react';
import { Shield, Moon, Sun, HelpCircle, Settings } from 'lucide-react';

interface HeaderProps {
    isDarkMode: boolean;
    toggleDarkMode: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isDarkMode, toggleDarkMode }) => {
    return (
        <header style={{
            height: 'var(--header-height)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 var(--spacing-lg)',
            backgroundColor: 'rgba(0, 86, 179, 0.85)', // var(--color-brand-blue) with alpha
            backdropFilter: 'var(--glass-blur)',
            WebkitBackdropFilter: 'var(--glass-blur)',
            color: 'white',
            boxShadow: 'var(--shadow-md)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            zIndex: 1000,
            position: 'relative',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                <Shield size={28} />
                <h1 style={{ color: 'white', fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.025em' }}>
                    CAMPUS DISPATCH COPILOT
                </h1>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                <button
                    onClick={toggleDarkMode}
                    style={{ color: 'white', display: 'flex', alignItems: 'center' }}
                    aria-label={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                >
                    {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>
                <button
                    style={{ color: 'white', display: 'flex', alignItems: 'center' }}
                    aria-label="Help and Documentation"
                >
                    <HelpCircle size={20} />
                </button>
                <button
                    style={{ color: 'white', display: 'flex', alignItems: 'center' }}
                    aria-label="Settings"
                >
                    <Settings size={20} />
                </button>
            </div>
        </header>
    );
};

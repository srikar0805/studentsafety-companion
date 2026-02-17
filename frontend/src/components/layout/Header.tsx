import React from 'react';
import { Shield, Moon, Sun, HelpCircle, Settings } from 'lucide-react';
import { useResponsive } from '../../hooks/useResponsive';

interface HeaderProps {
    isDarkMode: boolean;
    toggleDarkMode: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isDarkMode, toggleDarkMode }) => {
    const { isMobile } = useResponsive();

    return (
        <header style={{
            height: '64px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
            backgroundColor: isDarkMode ? 'rgba(15, 23, 42, 0.7)' : 'rgba(255, 255, 255, 0.7)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            color: 'var(--color-text-primary)',
            borderBottom: isDarkMode ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(0,0,0,0.05)',
            zIndex: 1100,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            transition: 'background-color 0.3s ease, border-color 0.3s ease'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    background: 'var(--color-brand-blue)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)'
                }}>
                    <Shield size={20} fill="currentColor" />
                </div>
                {!isMobile && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <h1 style={{
                            margin: 0,
                            fontSize: '15px',
                            fontWeight: 700,
                            letterSpacing: '-0.01em',
                            color: 'var(--color-text-primary)'
                        }}>
                            Campus Copilot
                        </h1>
                        <span style={{
                            fontSize: '11px',
                            color: 'var(--color-text-muted)',
                            fontWeight: 500,
                            letterSpacing: '0.02em'
                        }}>
                            STUDENT SAFETY SYSTEM
                        </span>
                    </div>
                )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                    onClick={toggleDarkMode}
                    className="header-btn"
                    title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                    style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '10px',
                        border: 'none',
                        background: 'transparent',
                        color: 'var(--color-text-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                    }}
                >
                    {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>
                <div style={{ width: '1px', height: '24px', background: 'var(--color-border-subtle)', margin: '0 4px' }} />
                <button
                    className="header-btn"
                    style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '10px',
                        border: 'none',
                        background: 'transparent',
                        color: 'var(--color-text-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                    }}
                >
                    <Settings size={20} />
                </button>
                <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #FF6B6B, #556270)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: 700,
                    marginLeft: '8px',
                    border: '2px solid white',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                    JD
                </div>
            </div>
            <style>{`
                .header-btn:hover {
                    background: var(--color-bg-subtle) !important;
                    color: var(--color-text-primary) !important;
                }
            `}</style>
        </header>
    );
};

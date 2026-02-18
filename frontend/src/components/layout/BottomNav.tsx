import React from 'react';
import { Home, MessageSquare, Map as MapIcon, User, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

interface BottomNavProps {
    activeTab: 'home' | 'chat' | 'map' | 'history' | 'profile';
    setActiveTab: (tab: any) => void;
    onSOS: () => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab, setActiveTab, onSOS }) => {
    const navItems = [
        { id: 'home', icon: Home, label: 'Home' },
        { id: 'chat', icon: MessageSquare, label: 'Chat' },
        { id: 'sos', icon: AlertTriangle, label: 'SOS', isAction: true },
        { id: 'map', icon: MapIcon, label: 'Map' },
        { id: 'profile', icon: User, label: 'Profile' },
    ];

    return (
        <nav style={{
            height: 'var(--bottom-nav-height)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-around',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'var(--glass-blur)',
            WebkitBackdropFilter: 'var(--glass-blur)',
            borderTop: '1px solid var(--glass-border)',
            paddingBottom: 'env(safe-area-inset-bottom)',
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: 1000,
            boxShadow: '0 -4px 16px rgba(0,0,0,0.05)'
        }}>
            {navItems.map(({ id, icon: Icon, label, isAction }) => {
                const isActive = activeTab === id;
                const isSOS = id === 'sos';

                return (
                    <button
                        key={id}
                        onClick={() => {
                            if (isAction && onSOS) {
                                onSOS();
                            } else {
                                setActiveTab(id);
                            }
                        }}
                        aria-label={label}
                        aria-current={isActive ? 'page' : undefined}
                        style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: '4px',
                            color: isSOS ? 'var(--color-safety-100)' : (isActive ? 'var(--color-primary)' : 'var(--color-text-muted)'),
                            transition: 'all 0.3s var(--ease-out)',
                            position: 'relative',
                            padding: '8px 12px',
                            borderRadius: 'var(--radius-md)',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer'
                        }}
                    >
                        {isActive && !isSOS && (
                            <motion.div
                                layoutId="nav-indicator"
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    right: 0,
                                    bottom: 0,
                                    backgroundColor: 'var(--color-primary-light)',
                                    borderRadius: 'var(--radius-md)',
                                    zIndex: -1
                                }}
                                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                            />
                        )}
                        <Icon size={24} strokeWidth={isActive || isSOS ? 2.5 : 2} fill={isSOS ? "currentColor" : "none"} />
                        <span style={{
                            fontSize: '10px',
                            fontWeight: isActive || isSOS ? 800 : 500,
                            letterSpacing: '0.02em',
                            textTransform: 'uppercase'
                        }}>
                            {label}
                        </span>
                    </button>
                );
            })}
        </nav>
    );
};

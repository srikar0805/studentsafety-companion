import React from 'react';
import { Home, Book, Dumbbell, Coffee, GraduationCap, Building2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface QuickActionsProps {
    onAction: (text: string) => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ onAction }) => {
    const actions = [
        { icon: Home, label: 'Go Home', text: 'Navigate to my dorm' },
        { icon: Book, label: 'Library', text: 'Route to Main Library' },
        { icon: Dumbbell, label: 'Gym', text: 'Go to Rec Center' },
        { icon: Coffee, label: 'Cafe', text: 'Find nearest coffee' },
        { icon: GraduationCap, label: 'Classes', text: 'Go to Science Hall' },
        { icon: Building2, label: 'Union', text: 'Student Union' },
    ];

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 }
    };

    return (
        <div style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <span style={{
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--color-text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                paddingLeft: '4px'
            }}>
                Quick Destinations
            </span>

            <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '12px'
                }}
            >
                {actions.map((action, index) => (
                    <motion.button
                        key={action.label}
                        variants={item}
                        onClick={() => onAction(action.text)}
                        whileHover={{ scale: 1.02, backgroundColor: 'var(--color-bg-secondary)' }}
                        whileTap={{ scale: 0.98 }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '16px',
                            backgroundColor: 'var(--glass-bg)',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '16px',
                            cursor: 'pointer',
                            textAlign: 'left',
                            color: 'var(--color-text-primary)',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
                        }}
                    >
                        <div style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '12px',
                            backgroundColor: `hsl(${210 + (index * 20)}, 90%, 96%)`, // Dynamic pastel blues/purples
                            color: `hsl(${210 + (index * 20)}, 80%, 50%)`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                        }}>
                            <action.icon size={20} />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                            <span style={{ fontSize: '14px', fontWeight: 600 }}>{action.label}</span>
                            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', opacity: 0.8 }}>
                                {action.text}
                            </span>
                        </div>
                    </motion.button>
                ))}
            </motion.div>
        </div>
    );
};

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot } from 'lucide-react';

export const LoadingState: React.FC = () => {
    const [statusIndex, setStatusIndex] = useState(0);
    const statuses = [
        'Checking recent incident reports...',
        'Analyzing campus patrol patterns...',
        'Finding the top 3 safest routes...',
        'Calculating risk scores for each path...',
        'Finalizing safety recommendations...'
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setStatusIndex((prev) => (prev + 1) % statuses.length);
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div
            role="status"
            aria-live="polite"
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 'var(--spacing-xl) var(--spacing-md)',
                gap: 'var(--spacing-md)'
            }}
        >
            <motion.div
                animate={{
                    scale: [1, 1.15, 1],
                    rotate: [0, 5, -5, 0]
                }}
                transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                style={{
                    width: '72px',
                    height: '72px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: 'var(--color-brand-blue-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-brand-blue)',
                    boxShadow: '0 0 20px var(--color-brand-blue-light)'
                }}
            >
                <Bot size={36} />
            </motion.div>

            <div style={{ textAlign: 'center', minHeight: '60px' }}>
                <AnimatePresence mode="wait">
                    <motion.p
                        key={statusIndex}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        style={{ fontWeight: 600, color: 'var(--color-gray-800)', margin: 0, fontSize: '15px' }}
                    >
                        {statuses[statusIndex]}
                    </motion.p>
                </AnimatePresence>
                <div style={{
                    display: 'flex',
                    gap: '6px',
                    justifyContent: 'center',
                    alignItems: 'center',
                    marginTop: '12px'
                }}>
                    {[0, 1, 2, 3].map((i) => (
                        <motion.div
                            key={i}
                            animate={{
                                scale: [1, 1.5, 1],
                                opacity: [0.3, 1, 0.3]
                            }}
                            transition={{
                                duration: 1.2,
                                repeat: Infinity,
                                delay: i * 0.2
                            }}
                            style={{
                                width: '6px',
                                height: '6px',
                                borderRadius: '50%',
                                backgroundColor: 'var(--color-brand-blue)'
                            }}
                        />
                    ))}
                </div>
            </div>

            <div style={{
                width: '240px',
                height: '6px',
                backgroundColor: 'var(--color-gray-200)',
                borderRadius: '3px',
                overflow: 'hidden',
                marginTop: 'var(--spacing-md)',
                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.1)'
            }}>
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 10, ease: "linear" }}
                    style={{
                        height: '100%',
                        background: 'linear-gradient(90deg, var(--color-brand-blue), #60a5fa)',
                    }}
                />
            </div>
        </div>
    );
};

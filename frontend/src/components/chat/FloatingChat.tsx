import React from 'react';
import { motion } from 'framer-motion';
import { Shield } from 'lucide-react';
import { useStore } from '../../hooks/useStore';
import { MessageBubble } from './MessageBubble';
import { InputArea } from './InputArea';
import { RouteCard } from './RouteCard';
import { RouteComparisonView } from './RouteComparisonView';
import { LoadingState } from '../shared/LoadingState';
import { RouteCardSkeleton } from '../shared/Skeleton';

interface FloatingChatProps {
    onSendMessage: (text: string) => Promise<void>;
}

export const FloatingChat: React.FC<FloatingChatProps> = ({ onSendMessage }) => {
    const {
        messages,
        isTyping,
        routes,
        selectedRouteId,
        setSelectedRouteId
    } = useStore();

    return (
        <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 100, damping: 20 }}
            style={{
                position: 'absolute',
                top: '88px',
                left: '24px',
                bottom: '24px',
                width: '420px',
                backgroundColor: 'var(--color-chat-bg)',
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                borderRadius: '24px',
                boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0,0,0,0.05)',
                border: '1px solid var(--color-chat-border)',
                display: 'flex',
                flexDirection: 'column',
                zIndex: 1000,
                overflow: 'hidden'
            }}
        >
            {/* Header / Top Bar */}
            <div style={{
                padding: '16px 24px',
                borderBottom: '1px solid rgba(0,0,0,0.05)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'var(--color-bg-secondary)'
            }}>
                <Shield size={20} color="var(--color-brand-blue)" fill="rgba(33, 150, 243, 0.1)" />
                <span style={{
                    fontWeight: 700,
                    color: 'var(--color-text-primary)',
                    fontSize: '15px',
                    letterSpacing: '0.5px'
                }}>
                    STUDENT SAFETY COMPANION
                </span>
            </div>

            {/* Messages Area */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '0 0 20px 0' }} className="chat-container">
                <div style={{ padding: '20px 0' }}>
                    {messages.map((m) => (
                        <MessageBubble key={m.id} message={m} />
                    ))}
                </div>

                {isTyping && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                        <LoadingState />
                        <div style={{ padding: '0 var(--spacing-md)' }}>
                            <RouteCardSkeleton />
                            <RouteCardSkeleton />
                        </div>
                    </div>
                )}

                {!isTyping && messages.length > 1 && (
                    <motion.div
                        initial="hidden"
                        animate="visible"
                        variants={{
                            hidden: { opacity: 0 },
                            visible: {
                                opacity: 1,
                                transition: {
                                    staggerChildren: 0.15,
                                    delayChildren: 0.2
                                }
                            }
                        }}
                    >
                        {routes.length > 0 && (
                            <motion.div
                                variants={{ hidden: { opacity: 0, x: -10 }, visible: { opacity: 1, x: 0 } }}
                                style={{
                                    padding: '0 var(--spacing-md)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    marginBottom: '12px',
                                    marginTop: '8px'
                                }}
                            >
                                <div style={{
                                    height: '1px',
                                    flex: 1,
                                    backgroundColor: 'var(--color-gray-200)'
                                }} />
                                <span style={{
                                    fontSize: '11px',
                                    fontWeight: 700,
                                    color: 'var(--color-gray-500)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '1px'
                                }}>
                                    Suggested Routes
                                </span>
                                <div style={{
                                    height: '1px',
                                    flex: 1,
                                    backgroundColor: 'var(--color-gray-200)'
                                }} />
                            </motion.div>
                        )}

                        {routes.map((r) => (
                            <motion.div
                                key={r.route.id}
                                variants={{
                                    hidden: { opacity: 0, y: 20, scale: 0.95 },
                                    visible: { opacity: 1, y: 0, scale: 1 }
                                }}
                                transition={{ type: 'spring', stiffness: 50, damping: 15 }}
                            >
                                <RouteCard
                                    rankedRoute={r}
                                    isSelected={selectedRouteId === r.route.id}
                                    onSelect={setSelectedRouteId}
                                />
                            </motion.div>
                        ))}

                        {routes.length >= 2 && (
                            <motion.div
                                variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
                                transition={{ delay: 0.6 }}
                            >
                                <RouteComparisonView recommended={routes[0]} alternative={routes[1]} />
                            </motion.div>
                        )}
                    </motion.div>
                )}
            </div>

            {/* Input Area */}
            <div style={{
                padding: '0',
                background: 'rgba(255,255,255,0.5)',
                borderTop: '1px solid rgba(0,0,0,0.05)'
            }}>
                <InputArea onSendMessage={onSendMessage} />
            </div>
        </motion.div>
    );
};

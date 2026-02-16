import React from 'react';
import type { Message } from '../../types/chat';
import { motion } from 'framer-motion';
import { User, Bot } from 'lucide-react';
import { format } from 'date-fns';

interface MessageBubbleProps {
    message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
    const isAssistant = message.role === 'assistant';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.3 }}
            style={{
                display: 'flex',
                flexDirection: isAssistant ? 'row' : 'row-reverse',
                alignItems: 'flex-end',
                gap: 'var(--spacing-sm)',
                margin: 'var(--spacing-md) 0',
                padding: `0 var(--spacing-md)`,
            }}
        >
            <div style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: isAssistant ? 'var(--color-gray-200)' : 'var(--color-brand-blue)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: isAssistant ? 'var(--color-gray-600)' : 'white',
                flexShrink: 0
            }}>
                {isAssistant ? <Bot size={18} /> : <User size={18} />}
            </div>

            <div style={{
                maxWidth: '75%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: isAssistant ? 'flex-start' : 'flex-end',
            }}>
                <div style={{
                    padding: '12px 18px',
                    borderRadius: '20px',
                    borderBottomLeftRadius: isAssistant ? '4px' : '20px',
                    borderBottomRightRadius: isAssistant ? '20px' : '4px',
                    background: isAssistant
                        ? 'linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-gray-100) 100%)'
                        : 'linear-gradient(135deg, var(--color-brand-blue) 0%, var(--color-brand-blue-dark) 100%)',
                    color: isAssistant ? 'var(--color-gray-900)' : 'white',
                    fontSize: '15px',
                    boxShadow: isAssistant ? '0 4px 15px rgba(0,0,0,0.03)' : '0 4px 15px rgba(0, 86, 179, 0.2)',
                    lineHeight: 1.5,
                    border: isAssistant ? '1px solid var(--color-gray-200)' : 'none',
                }}>
                    {message.content}
                </div>
                <span style={{
                    fontSize: '11px',
                    color: 'var(--color-gray-500)',
                    marginTop: '4px',
                    padding: '0 4px'
                }}>
                    {format(message.timestamp, 'h:mm a')}
                </span>
            </div>
        </motion.div>
    );
};

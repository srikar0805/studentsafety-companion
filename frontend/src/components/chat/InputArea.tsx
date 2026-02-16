import React, { useState } from 'react';
import { Send, Mic, Paperclip, Home, Book, Pizza, Landmark } from 'lucide-react';

interface InputAreaProps {
    onSendMessage: (text: string) => void;
}

export const InputArea: React.FC<InputAreaProps> = ({ onSendMessage }) => {
    const [text, setText] = useState('');

    const suggestions = [
        { label: 'To my dorm', icon: Home },
        { label: 'Library', icon: Book },
        { label: 'Grab food', icon: Pizza },
        { label: 'Tiger statue', icon: Landmark },
    ];

    const handleSend = () => {
        if (text.trim()) {
            onSendMessage(text);
            setText('');
        }
    };

    return (
        <div style={{
            padding: 'var(--spacing-md)',
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            backdropFilter: 'var(--glass-blur)',
            WebkitBackdropFilter: 'var(--glass-blur)',
            borderTop: '1px solid var(--glass-border)',
            boxShadow: '0 -4px 20px rgba(0,0,0,0.03)'
        }}>
            {/* Suggestion Chips */}
            <div style={{
                display: 'flex',
                gap: 'var(--spacing-sm)',
                overflowX: 'auto',
                paddingBottom: 'var(--spacing-md)',
                scrollbarWidth: 'none',
                msOverflowStyle: 'none'
            }}>
                {suggestions.map(({ label, icon: Icon }) => (
                    <button
                        key={label}
                        onClick={() => setText(label)}
                        style={{
                            flexShrink: 0,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '6px 14px',
                            borderRadius: 'var(--radius-full)',
                            backgroundColor: 'var(--color-gray-100)',
                            color: 'var(--color-gray-700)',
                            fontSize: '13px',
                            fontWeight: 500,
                            transition: 'all 0.2s ease',
                        }}
                    >
                        <Icon size={14} />
                        {label}
                    </button>
                ))}
            </div>

            {/* Input Box */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                backgroundColor: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-lg)',
                padding: '8px 12px',
                border: '1.5px solid transparent',
                transition: 'all 0.2s ease',
            }}>
                <button
                    style={{ color: 'var(--color-text-muted)' }}
                    aria-label="Attach file"
                >
                    <Paperclip size={20} />
                </button>
                <label htmlFor="destination-input" className="sr-only">Where do you need to go?</label>
                <input
                    id="destination-input"
                    type="text"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Where do you need to go?"
                    aria-describedby="input-help"
                    style={{
                        flex: 1,
                        background: 'none',
                        border: 'none',
                        outline: 'none',
                        fontSize: '15px',
                        color: 'var(--color-text-primary)',
                        padding: '4px 0'
                    }}
                />
                <span id="input-help" className="sr-only">Enter a building name or address on campus</span>
                <button
                    style={{ color: 'var(--color-text-muted)' }}
                    aria-label="Voice input"
                >
                    <Mic size={20} />
                </button>
                <button
                    onClick={handleSend}
                    disabled={!text.trim()}
                    style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: text.trim() ? 'var(--color-brand-blue)' : 'var(--color-gray-300)',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s ease',
                        cursor: text.trim() ? 'pointer' : 'default'
                    }}
                >
                    <Send size={18} fill="white" />
                </button>
            </div>
        </div>
    );
};

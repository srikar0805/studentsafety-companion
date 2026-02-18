import React, { useState } from 'react';
import type { LocationOption } from '../../types/disambiguation';
import { MapPin, Navigation } from 'lucide-react';
import './DisambiguationDialog.css';

interface DisambiguationDialogProps {
    category: string;
    question: string;
    options: LocationOption[];
    onSelectLocation: (location: LocationOption) => void;
    onCancel: () => void;
}

export const DisambiguationDialog: React.FC<DisambiguationDialogProps> = ({
    category,
    question,
    options,
    onSelectLocation,
    onCancel,
}) => {
    const categoryEmojis: Record<string, string> = {
        dorm: '🏠',
        library: '📚',
        dining: '🍽️',
        academic: '🎓',
        recreation: '🏃',
        parking: '🚗',
    };

    const emoji = categoryEmojis[category] || '📍';

    const [showOtherInput, setShowOtherInput] = useState(false);
    const [otherValue, setOtherValue] = useState("");
    const [otherError, setOtherError] = useState("");

    const handleOtherSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!otherValue.trim()) {
            setOtherError("Please enter a location name.");
            return;
        }
        // Pass a minimal LocationOption (name + category)
        onSelectLocation({
            name: otherValue.trim(),
            address: undefined,
            coordinates: undefined as any, // will be resolved later
            category,
            distance_meters: undefined,
        });
    };

    return (
        <div className="disambiguation-overlay">
            <div className="disambiguation-dialog">
                <div className="disambiguation-header">
                    <span className="category-emoji">{emoji}</span>
                    <h3>{question}</h3>
                </div>

                <div className="location-options">
                    {options.map((option, index) => (
                        <button
                            key={index}
                            className="location-option"
                            onClick={() => onSelectLocation(option)}
                        >
                            <div className="option-icon">
                                <MapPin size={18} />
                            </div>
                            <div className="option-details">
                                <div className="option-name">{option.name}</div>
                                {option.address && (
                                    <div className="option-address">{option.address}</div>
                                )}
                                {option.distance_meters && (
                                    <div className="option-distance">
                                        <Navigation size={12} />
                                        {(option.distance_meters / 1000).toFixed(1)} km away
                                    </div>
                                )}
                            </div>
                        </button>
                    ))}
                    {/* Other option */}
                    {!showOtherInput ? (
                        <button
                            className="location-option other-option"
                            onClick={() => setShowOtherInput(true)}
                        >
                            <div className="option-icon">
                                <MapPin size={18} />
                            </div>
                            <div className="option-details">
                                <div className="option-name">Other...</div>
                                <div className="option-address">Type a different location</div>
                            </div>
                        </button>
                    ) : (
                        <form className="other-input-form" onSubmit={handleOtherSubmit}>
                            <input
                                type="text"
                                className="other-input"
                                placeholder="Enter location name"
                                value={otherValue}
                                onChange={e => { setOtherValue(e.target.value); setOtherError(""); }}
                                autoFocus
                            />
                            <button type="submit" className="other-submit">OK</button>
                            <button type="button" className="other-cancel" onClick={() => { setShowOtherInput(false); setOtherValue(""); setOtherError(""); }}>Cancel</button>
                            {otherError && <div className="other-error">{otherError}</div>}
                        </form>
                    )}
                </div>

                <button className="cancel-button" onClick={onCancel}>
                    Cancel
                </button>
            </div>
        </div>
    );
};

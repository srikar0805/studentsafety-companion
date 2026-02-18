import React, { useState } from 'react';
import { Footprints, Bike, Car, Bus } from 'lucide-react';
import type { TransportationMode } from '../../types/disambiguation';
import './TransportationModeSelector.css';

interface TransportationModeSelectorProps {
    onSelectMode: (mode: TransportationMode) => void;
    selectedMode?: TransportationMode;
}

interface ModeOption {
    mode: TransportationMode;
    Icon: React.ElementType;
    label: string;
    description: string;
}

const modeOptions: ModeOption[] = [
    {
        mode: 'foot',
        Icon: Footprints,
        label: 'Walk',
        description: 'Walking',
    },
    {
        mode: 'bike',
        Icon: Bike,
        label: 'Bike',
        description: 'Cycling',
    },
    {
        mode: 'car',
        Icon: Car,
        label: 'Drive',
        description: 'Driving',
    },
    {
        mode: 'bus',
        Icon: Bus,
        label: 'Bus',
        description: 'Public Transit',
    },
];

export const TransportationModeSelector: React.FC<TransportationModeSelectorProps> = ({
    onSelectMode,
    selectedMode = 'foot',
}) => {
    const [hoveredMode, setHoveredMode] = useState<TransportationMode | null>(null);

    return (
        <div className="mode-selector-container">
            <div className="mode-selector-header">
                <h4>How would you like to travel?</h4>
            </div>
            <div className="mode-selector-options">
                {modeOptions.map(({ mode, Icon, label, description }) => (
                    <button
                        key={mode}
                        className={`mode-option ${selectedMode === mode ? 'selected' : ''}`}
                        onClick={() => onSelectMode(mode)}
                        onMouseEnter={() => setHoveredMode(mode)}
                        onMouseLeave={() => setHoveredMode(null)}
                    >
                        <div className="mode-icon">
                            <Icon size={24} />
                        </div>
                        <div className="mode-label">{label}</div>
                        {(hoveredMode === mode || selectedMode === mode) && (
                            <div className="mode-description">{description}</div>
                        )}
                    </button>
                ))}
            </div>
        </div>
    );
};

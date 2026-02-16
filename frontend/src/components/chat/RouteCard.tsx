import React from 'react';
import type { RankedRoute } from '../../types/route';
import { SafetyScoreCircle } from '../shared/SafetyScoreCircle';
import { Clock, CheckCircle2, AlertTriangle, Navigation, Map as MapIcon } from 'lucide-react';
import { getSafetyDetails } from '../../utils/formatters';
import { motion } from 'framer-motion';

interface RouteCardProps {
    rankedRoute: RankedRoute;
    isSelected: boolean;
    onSelect: (id: string) => void;
}

export const RouteCard: React.FC<RouteCardProps> = ({ rankedRoute, isSelected, onSelect }) => {
    const { safety_analysis, duration_minutes, distance_meters, explanation, rank } = rankedRoute;
    const isRecommended = rank === 1;
    const { color } = getSafetyDetails(safety_analysis.risk_score);

    return (
        <motion.div
            whileHover={{ y: -4, boxShadow: '0 12px 24px rgba(0,0,0,0.1)' }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSelect(rankedRoute.route.id)}
            role="button"
            tabIndex={0}
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            aria-label={`Route via ${rankedRoute.route.id === 'route_1' ? 'Conley Avenue' : 'Parking Lot Shortcut'}, ${duration_minutes} minutes, risk score ${safety_analysis.risk_score} out of 100`}
=======
            aria-label={`Route option ${rank}, ${duration_minutes} minutes, risk score ${safety_analysis.risk_score} out of 100`}
>>>>>>> Stashed changes
=======
            aria-label={`Route option ${rank}, ${duration_minutes} minutes, risk score ${safety_analysis.risk_score} out of 100`}
>>>>>>> Stashed changes
=======
            aria-label={`Route option ${rank}, ${duration_minutes} minutes, risk score ${safety_analysis.risk_score} out of 100`}
>>>>>>> Stashed changes
=======
            aria-label={`Route option ${rank}, ${duration_minutes} minutes, risk score ${safety_analysis.risk_score} out of 100`}
>>>>>>> Stashed changes
            onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelect(rankedRoute.route.id)}
            style={{
                backgroundColor: isRecommended ? 'rgba(0, 135, 90, 0.02)' : 'var(--color-bg-primary)',
                borderLeft: `6px solid ${color}`,
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--spacing-lg)',
                margin: 'var(--spacing-md)',
                cursor: 'pointer',
                boxShadow: isSelected ? `0 0 0 2px var(--color-primary), var(--shadow-card)` : 'var(--shadow-sm)',
                position: 'relative',
                transition: 'all 0.3s var(--ease-out)',
                border: '1px solid var(--color-border-light)',
                overflow: 'hidden'
            }}
        >
            {isRecommended && (
                <div style={{
                    position: 'absolute',
                    top: '0',
                    right: '0',
                    backgroundColor: 'var(--color-safety-0)',
                    color: 'white',
                    padding: '4px 16px',
                    borderBottomLeftRadius: 'var(--radius-md)',
                    fontSize: '10px',
                    fontWeight: 900,
                    letterSpacing: '0.05em',
                    boxShadow: 'var(--shadow-sm)',
                    textTransform: 'uppercase'
                }}>
                    BEST OPTION
                </div>
            )}

            <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                <div style={{ flexShrink: 0 }}>
                    <SafetyScoreCircle score={safety_analysis.risk_score} size={80} />
                </div>

                <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '4px', color: 'var(--color-gray-900)' }}>
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                        Via {rankedRoute.route.id === 'route_1' ? 'Conley Avenue' : 'Parking Lot Shortcut'}
=======
                        Route Option {rank}
>>>>>>> Stashed changes
=======
                        Route Option {rank}
>>>>>>> Stashed changes
=======
                        Route Option {rank}
>>>>>>> Stashed changes
=======
                        Route Option {rank}
>>>>>>> Stashed changes
                    </h3>

                    <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginBottom: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-gray-600)', fontSize: '13px' }}>
                            <Clock size={14} />
                            <span>{duration_minutes} mins</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-gray-600)', fontSize: '13px' }}>
                            <Navigation size={14} />
                            <span>{distance_meters}m</span>
                        </div>
                    </div>

                    <p style={{ fontSize: '13px', color: 'var(--color-gray-700)', marginBottom: '16px', lineHeight: 1.4 }}>
                        {explanation}
                    </p>

                    <div style={{ borderTop: '1px solid var(--color-gray-100)', paddingTop: '12px' }}>
                        <h4 style={{ fontSize: '12px', fontWeight: 700, marginBottom: '8px', color: 'var(--color-gray-800)' }}>
                            {safety_analysis.concerns.length > 0 ? 'CONCERNS' : 'WHY THIS ROUTE?'}
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                            {(safety_analysis.positives.length > 0 ? safety_analysis.positives : safety_analysis.concerns).map((item, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'start', gap: '8px', fontSize: '12px', color: 'var(--color-gray-600)' }}>
                                    {safety_analysis.positives.length > 0 ?
                                        <CheckCircle2 size={14} color="var(--color-safety-0)" style={{ marginTop: '2px' }} /> :
                                        <AlertTriangle size={14} color="var(--color-safety-80)" style={{ marginTop: '2px' }} />
                                    }
                                    <span>{item}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginTop: '20px' }}>
                        <button style={{
                            flex: 1,
                            padding: '8px',
                            borderRadius: 'var(--radius-sm)',
                            border: '1.5px solid var(--color-brand-blue)',
                            color: 'var(--color-brand-blue)',
                            fontSize: '13px',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '6px'
                        }}>
                            <MapIcon size={16} />
                            View Map
                        </button>
                        <button style={{
                            flex: 1,
                            padding: '8px',
                            borderRadius: 'var(--radius-sm)',
                            backgroundColor: 'var(--color-brand-blue)',
                            color: 'white',
                            fontSize: '13px',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '6px'
                        }}>
                            Start
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

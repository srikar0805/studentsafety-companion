import React from 'react';
import type { RankedRoute } from '../../types/route';
import { TrendingUp, TrendingDown, Clock, Shield } from 'lucide-react';

interface RouteComparisonViewProps {
    recommended: RankedRoute;
    alternative: RankedRoute;
}

export const RouteComparisonView: React.FC<RouteComparisonViewProps> = ({ recommended, alternative }) => {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    const timeDiff = recommended.duration_minutes - alternative.duration_minutes;
    const safetyImprovement = alternative.safety_analysis.risk_score - recommended.safety_analysis.risk_score;
=======
    const timeDiff = recommended.time_tradeoff_minutes ?? (recommended.duration_minutes - alternative.duration_minutes);
    const safetyImprovement = recommended.safety_improvement_percent
        ?? (alternative.safety_analysis.risk_score - recommended.safety_analysis.risk_score);
>>>>>>> Stashed changes
=======
    const timeDiff = recommended.time_tradeoff_minutes ?? (recommended.duration_minutes - alternative.duration_minutes);
    const safetyImprovement = recommended.safety_improvement_percent
        ?? (alternative.safety_analysis.risk_score - recommended.safety_analysis.risk_score);
>>>>>>> Stashed changes

    return (
        <div style={{
            padding: 'var(--spacing-md)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-md)',
            backgroundColor: 'var(--color-gray-50)',
            borderRadius: 'var(--radius-md)',
            margin: 'var(--spacing-md)'
        }}>
            <h3 style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-gray-500)', textAlign: 'center' }}>
                ROUTE COMPARISON
            </h3>

            <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                {/* Recommendation Summary */}
                <div style={{ flex: 1, backgroundColor: 'white', padding: '12px', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-sm)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-safety-0)', marginBottom: '8px' }}>
                        <Shield size={16} />
                        <span style={{ fontSize: '12px', fontWeight: 700 }}>SAFER</span>
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 800 }}>{recommended.safety_analysis.risk_score}/100</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-gray-500)' }}>Risk Score</div>
                </div>

                {/* Alternative Summary */}
                <div style={{ flex: 1, backgroundColor: 'white', padding: '12px', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-sm)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-brand-blue)', marginBottom: '8px' }}>
                        <Clock size={16} />
                        <span style={{ fontSize: '12px', fontWeight: 700 }}>FASTER</span>
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 800 }}>{alternative.duration_minutes} min</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-gray-500)' }}>Total Time</div>
                </div>
            </div>

            <div style={{
                padding: '12px',
                backgroundColor: 'var(--color-brand-blue-light)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '13px', color: 'var(--color-brand-blue)', fontWeight: 600 }}>Safety Gain</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-safety-0)', fontWeight: 800 }}>
                        <TrendingDown size={16} />
                        <span>{safetyImprovement} points safer</span>
                    </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '13px', color: 'var(--color-brand-blue)', fontWeight: 600 }}>Time Trade-off</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-safety-80)', fontWeight: 800 }}>
                        <TrendingUp size={16} />
                        <span>+{timeDiff} minutes longer</span>
                    </div>
                </div>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--color-gray-600)', fontStyle: 'italic', textAlign: 'center' }}>
                "Given the current conditions, the 45% safety improvement outweighs the 2-minute time saving."
            </p>
        </div>
    );
};

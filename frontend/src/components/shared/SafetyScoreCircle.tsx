import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getSafetyDetails } from '../../utils/formatters';

interface SafetyScoreCircleProps {
    score: number;
    size?: number;
}

export const SafetyScoreCircle: React.FC<SafetyScoreCircleProps> = ({ score, size = 100 }) => {
    const [displayScore, setDisplayScore] = useState(0);
    const { color, label } = getSafetyDetails(score);

    const strokeWidth = size * 0.1;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;

    useEffect(() => {
        // Count up animation
        const end = score;
        const duration = 1500;
        const startTime = performance.now();

        const animate = (currentTime: number) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Power3 ease out
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentScore = Math.floor(easeProgress * end);

            setDisplayScore(currentScore);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [score]);

    const offset = circumference - (score / 100) * circumference;

    return (
        <div
            role="progressbar"
            aria-valuenow={score}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Safety score: ${score} out of 100. Status: ${label}`}
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--spacing-xs)'
            }}
        >
            <div style={{ position: 'relative', width: size, height: size }}>
                <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
                    {/* Background circle */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="transparent"
                        stroke="var(--color-gray-200)"
                        strokeWidth={strokeWidth}
                    />
                    {/* Progress circle */}
                    <motion.circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="transparent"
                        stroke={color}
                        strokeWidth={strokeWidth}
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{
                            strokeDashoffset: offset,
                            filter: [`drop-shadow(0 0 2px ${color}40)`, `drop-shadow(0 0 8px ${color}80)`, `drop-shadow(0 0 2px ${color}40)`]
                        }}
                        transition={{
                            strokeDashoffset: { type: 'spring', stiffness: 50, damping: 15, delay: 0.2 },
                            filter: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                        }}
                        strokeLinecap="round"
                    />
                </svg>
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <span style={{ fontSize: size * 0.28, fontWeight: 800, color: 'var(--color-gray-900)' }}>{displayScore}</span>
                    <span style={{ fontSize: size * 0.1, color: 'var(--color-gray-500)', fontWeight: 600 }}>/100</span>
                </div>
            </div>
            <span style={{
                color,
                fontWeight: 800,
                fontSize: size * 0.1,
                letterSpacing: '0.05em',
                marginTop: '2px'
            }}>
                {label}
            </span>
        </div>
    );
};

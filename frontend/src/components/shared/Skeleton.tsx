import React from 'react';
import { motion } from 'framer-motion';

interface SkeletonProps {
    width?: string | number;
    height?: string | number;
    borderRadius?: string | number;
    className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
    width = '100%',
    height = '1rem',
    borderRadius = 'var(--radius-sm)',
    className = ''
}) => {
    return (
        <div
            className={`skeleton ${className}`}
            style={{
                width,
                height,
                borderRadius,
                background: 'linear-gradient(90deg, var(--color-bg-tertiary) 25%, var(--color-border-light) 50%, var(--color-bg-tertiary) 75%)',
                backgroundSize: '200% 100%',
                position: 'relative',
                overflow: 'hidden'
            }}
        >
            <motion.div
                animate={{
                    x: ['-100%', '100%']
                }}
                transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'linear'
                }}
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)'
                }}
            />
        </div>
    );
};

export const RouteCardSkeleton: React.FC = () => {
    return (
        <div style={{
            backgroundColor: 'var(--color-bg-secondary)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-lg)',
            margin: 'var(--spacing-md)',
            border: '1px solid var(--color-gray-100)',
            display: 'flex',
            gap: 'var(--spacing-md)'
        }}>
            <Skeleton width={80} height={80} borderRadius="var(--radius-full)" />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                <Skeleton width="60%" height="1.25rem" />
                <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                    <Skeleton width="40px" height="0.875rem" />
                    <Skeleton width="40px" height="0.875rem" />
                </div>
                <Skeleton width="100%" height="3rem" />
                <div style={{ borderTop: '1px solid var(--color-gray-100)', paddingTop: 'var(--spacing-md)', marginTop: 'var(--spacing-sm)' }}>
                    <Skeleton width="30%" height="0.75rem" />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)', marginTop: 'var(--spacing-sm)' }}>
                        <Skeleton width="90%" height="0.75rem" />
                        <Skeleton width="85%" height="0.75rem" />
                    </div>
                </div>
                <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-md)' }}>
                    <Skeleton width="50%" height="36px" borderRadius="var(--radius-sm)" />
                    <Skeleton width="50%" height="36px" borderRadius="var(--radius-sm)" />
                </div>
            </div>
        </div>
    );
};

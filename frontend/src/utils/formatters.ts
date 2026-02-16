export const getSafetyDetails = (score: number) => {
    if (score <= 20) return { color: 'var(--color-safety-0)', label: 'VERY SAFE', border: 'var(--color-safety-0)' };
    if (score <= 40) return { color: 'var(--color-safety-40)', label: 'SAFE', border: 'var(--color-safety-40)' };
    if (score <= 60) return { color: 'var(--color-safety-60)', label: 'MODERATE', border: 'var(--color-safety-60)' };
    if (score <= 80) return { color: 'var(--color-safety-80)', label: 'CAUTION', border: 'var(--color-safety-80)' };
    return { color: 'var(--color-safety-100)', label: 'AVOID', border: 'var(--color-safety-100)' };
};

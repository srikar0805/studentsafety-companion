import { useState, useEffect } from 'react';

export const BREAKPOINTS = {
    mobile: 0,
    tablet: 768,
    desktop: 1024,
    wide: 1440,
} as const;

export const useResponsive = () => {
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);

    useEffect(() => {
        const handleResize = () => setWindowWidth(window.innerWidth);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return {
        isMobile: windowWidth < BREAKPOINTS.tablet,
        isTablet: windowWidth >= BREAKPOINTS.tablet && windowWidth < BREAKPOINTS.desktop,
        isDesktop: windowWidth >= BREAKPOINTS.desktop,
        windowWidth,
    };
};

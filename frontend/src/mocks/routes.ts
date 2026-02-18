import type { RankedRoute } from '../types/route';

export const MOCK_ROUTES: RankedRoute[] = [
    {
        rank: 1,
        route: {
            id: 'route_1',
            geometry: {
                type: 'LineString',
                coordinates: [
                    [-92.3268, 38.9448],
                    [-92.3266, 38.9446],
                    [-92.3260, 38.9445],
                    [-92.3255, 38.9448]
                ]
            },
            distance_meters: 850,
            duration_seconds: 480,
            waypoints: [
                { latitude: 38.9448, longitude: -92.3268 },
                { latitude: 38.9448, longitude: -92.3255 }
            ]
        },
        safety_analysis: {
            risk_score: 15,
            risk_level: 'Very Safe',
            incident_count: 0,
            emergency_phones: 2,
            lighting_quality: 'good',
            patrol_frequency: 'high',
            concerns: [],
            positives: [
                'Well-lit main pathway',
                '2 emergency call boxes',
                'Zero incidents in past 30 days',
                'High police patrol factor'
            ]
        },
        duration_minutes: 8,
        distance_meters: 850,
        explanation: 'I recommend taking the longer route via Conley Avenue. This path is well-lit with 2 emergency call boxes and zero incidents reported recently.'
    },
    {
        rank: 2,
        route: {
            id: 'route_2',
            geometry: {
                type: 'LineString',
                coordinates: [
                    [-92.3268, 38.9448],
                    [-92.3260, 38.9455],
                    [-92.3255, 38.9448]
                ]
            },
            distance_meters: 650,
            duration_seconds: 360,
            waypoints: [
                { latitude: 38.9448, longitude: -92.3268 },
                { latitude: 38.9448, longitude: -92.3255 }
            ]
        },
        safety_analysis: {
            risk_score: 65,
            risk_level: 'Caution',
            incident_count: 1,
            emergency_phones: 0,
            lighting_quality: 'poor',
            patrol_frequency: 'low',
            concerns: [
                '1 theft reported last week',
                'Poor lighting in parking area',
                'Low patrol frequency'
            ],
            positives: [
                'Fastest connection'
            ]
        },
        duration_minutes: 6,
        distance_meters: 650,
        explanation: 'This shortcut through the parking lot is 2 minutes faster but has significantly higher risk due to poor lighting and a recent incident.'
    }
];

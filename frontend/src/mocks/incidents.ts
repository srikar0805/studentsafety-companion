import type { Incident, EmergencyPhone } from '../types/incident';

export const MOCK_INCIDENTS: Incident[] = [
    {
        id: 'incident_1',
        type: 'Theft',
        location: { latitude: 38.9446, longitude: -92.3266 },
        date: '2026-02-10T23:45:00Z',
        description: 'Bike theft reported near the library entrance.',
        severity: 'medium'
    },
    {
        id: 'incident_2',
        type: 'Vandalism',
        location: { latitude: 38.9450, longitude: -92.3270 },
        date: '2026-02-12T02:15:00Z',
        description: 'Graffiti on building exterior.',
        severity: 'low'
    }
];

export const MOCK_PHONES: EmergencyPhone[] = [
    {
        id: 'phone_1',
        location: { latitude: 38.9448, longitude: -92.3268 },
        name: 'Box #104'
    },
    {
        id: 'phone_2',
        location: { latitude: 38.9440, longitude: -92.3250 },
        name: 'Box #215'
    }
];

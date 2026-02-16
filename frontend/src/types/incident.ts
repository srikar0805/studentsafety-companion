import type { Coordinates } from './coordinates';

export interface Incident {
    id: string;
    type: string; // "theft", "assault", "vandalism"
    location: Coordinates;
    date: string; // ISO 8601
    description: string;
    severity: 'low' | 'medium' | 'high';
}

export interface EmergencyPhone {
<<<<<<< Updated upstream
    id: string;
    location: Coordinates;
    name: string;
=======
    id?: string;
    location: Coordinates;
    name?: string;
>>>>>>> Stashed changes
}

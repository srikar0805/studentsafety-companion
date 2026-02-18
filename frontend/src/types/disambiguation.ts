import type { Coordinates } from './coordinates';

export interface LocationOption {
    name: string;
    address?: string;
    coordinates: Coordinates;
    distance_meters?: number;
    category: string;
}

export interface DisambiguationResponse {
    response_type: 'disambiguation';
    category: string;
    question: string;
    options: LocationOption[];
}

export type TransportationMode = 'foot' | 'bike' | 'car' | 'bus';

export interface ModeSelectionRequest {
    origin: string | Coordinates;
    destination: string | Coordinates;
    mode?: TransportationMode;
}

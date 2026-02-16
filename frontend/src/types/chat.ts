import type { Coordinates } from './coordinates';

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export interface RouteRequest {
    origin: Coordinates;
    destination: Coordinates;
    priority: 'safety' | 'speed' | 'balanced';
    time: Date;
    concerns: string[];
}

import type { Coordinates } from './coordinates';

export interface Route {
  id: string;
  geometry: {
    type: 'LineString';
    coordinates: [number, number][]; // [lon, lat] pairs
  };
  distance_meters: number;
  duration_seconds: number;
  waypoints: Coordinates[];
}

export interface SafetyAnalysis {
  risk_score: number; // 0-100
  risk_level: 'Very Safe' | 'Safe' | 'Moderate' | 'Caution' | 'High Risk';
  incident_count: number;
  emergency_phones: number;
  lighting_quality: 'good' | 'moderate' | 'poor';
  patrol_frequency: 'high' | 'moderate' | 'low';
  concerns: string[];
  positives: string[];
}

export interface RankedRoute {
  rank: number;
  route: Route;
  safety_analysis: SafetyAnalysis;
  duration_minutes: number;
  distance_meters: number;
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
  safety_improvement_percent?: number;
  time_tradeoff_minutes?: number;
>>>>>>> Stashed changes
=======
  safety_improvement_percent?: number;
  time_tradeoff_minutes?: number;
>>>>>>> Stashed changes
=======
  safety_improvement_percent?: number;
  time_tradeoff_minutes?: number;
>>>>>>> Stashed changes
  explanation: string;
}

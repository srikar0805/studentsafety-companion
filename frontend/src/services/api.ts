/**
 * API client for Campus Safety Dispatch backend
 */

import type { RankedRoute } from '../types/route';
import type { Incident } from '../types/incident';
import type { Coordinates } from '../types/coordinates';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface DispatchRequest {
  message: string;
}

export interface DispatchResponse {
  response?: string;
  response_type?: 'routes' | 'disambiguation';
  // Disambiguation fields
  category?: string;
  question?: string;
  options?: Array<{
    name: string;
    address?: string;
    coordinates: Coordinates;
    distance_meters?: number;
    category: string;
  }>;
}

export interface RouteRequest {
  origin: Coordinates | string;
  destination: Coordinates | string;
  user_mode?: 'student' | 'community';
  priority?: 'safety' | 'speed' | 'balanced';
  time?: string;
  concerns?: string[];
  force_refresh?: boolean;
  transportation_mode?: 'foot' | 'bike' | 'car' | 'bus';
}

export interface RoutesResponse {
  request_id: string;
  recommendation: {
    routes: RankedRoute[];
    primary_recommendation: RankedRoute;
    explanation: string;
    comparison: string;
  };
  incidents: Incident[];
  emergency_phones: Coordinates[];
}

/**
 * Send a message to the AI dispatch agent
 */
export async function sendDispatchMessage(message: string): Promise<DispatchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/dispatch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed: ${response.status} - ${errorText}`);
  }

  return response.json();
}

/**
 * Request ranked routes and safety analysis
 */
export async function fetchRoutes(request: RouteRequest): Promise<RoutesResponse> {
  const response = await fetch(`${API_BASE_URL}/api/routes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Routes request failed: ${response.status} - ${errorText}`);
  }

  return response.json();
}

/**
 * Health check endpoint
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json();
}

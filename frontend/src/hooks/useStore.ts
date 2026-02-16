import { create } from 'zustand';
import type { Message } from '../types/chat';
import type { RankedRoute } from '../types/route';
import { MOCK_ROUTES } from '../mocks/routes';
import { MOCK_INCIDENTS, MOCK_PHONES } from '../mocks/incidents';
import type { Incident, EmergencyPhone } from '../types/incident';

interface AppState {
    // Chat
    messages: Message[];
    addMessage: (message: Message) => void;
    isTyping: boolean;
    setIsTyping: (isTyping: boolean) => void;

    // Routes
    routes: RankedRoute[];
    selectedRouteId: string | null;
    setSelectedRouteId: (id: string | null) => void;

    // Safety Data
    incidents: Incident[];
    emergencyPhones: EmergencyPhone[];

    // Preferences
    isDarkMode: boolean;
    toggleDarkMode: () => void;
    userLocation: { latitude: number; longitude: number } | null;
    setUserLocation: (location: { latitude: number; longitude: number }) => void;
}

export const useStore = create<AppState>((set) => ({
    messages: [
        {
            id: '1',
            role: 'assistant',
            content: 'Hello! I am your Campus Dispatch Copilot. Where do you need to go safely today?',
            timestamp: new Date(),
        }
    ],
    addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
    isTyping: false,
    setIsTyping: (isTyping) => set({ isTyping }),

    routes: MOCK_ROUTES,
    selectedRouteId: 'route_1',
    setSelectedRouteId: (id) => set({ selectedRouteId: id }),

    incidents: MOCK_INCIDENTS,
    emergencyPhones: MOCK_PHONES,

    isDarkMode: false,
    toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
    userLocation: { latitude: 38.9446, longitude: -92.3266 }, // Mock location
    setUserLocation: (location) => set({ userLocation: location }),
}));

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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
    setRoutes: (routes: RankedRoute[]) => void;
>>>>>>> Stashed changes
=======
    setRoutes: (routes: RankedRoute[]) => void;
>>>>>>> Stashed changes
=======
    setRoutes: (routes: RankedRoute[]) => void;
>>>>>>> Stashed changes

    // Safety Data
    incidents: Incident[];
    emergencyPhones: EmergencyPhone[];
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
    setIncidents: (incidents: Incident[]) => void;
    setEmergencyPhones: (phones: EmergencyPhone[]) => void;
>>>>>>> Stashed changes
=======
    setIncidents: (incidents: Incident[]) => void;
    setEmergencyPhones: (phones: EmergencyPhone[]) => void;
>>>>>>> Stashed changes
=======
    setIncidents: (incidents: Incident[]) => void;
    setEmergencyPhones: (phones: EmergencyPhone[]) => void;
>>>>>>> Stashed changes

    // Preferences
    isDarkMode: boolean;
    toggleDarkMode: () => void;
    userLocation: { latitude: number; longitude: number } | null;
    setUserLocation: (location: { latitude: number; longitude: number }) => void;
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

    // Map Layers
    layerVisibility: {
        routes: boolean;
        incidents: boolean;
        phones: boolean;
        patrolZones: boolean;
    };
    toggleLayer: (layer: "routes" | "incidents" | "phones" | "patrolZones") => void;
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream

    incidents: MOCK_INCIDENTS,
    emergencyPhones: MOCK_PHONES,
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    setRoutes: (routes) => set({ routes }),

    incidents: MOCK_INCIDENTS,
    emergencyPhones: MOCK_PHONES,
    setIncidents: (incidents) => set({ incidents }),
    setEmergencyPhones: (phones) => set({ emergencyPhones: phones }),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

    isDarkMode: false,
    toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
    userLocation: { latitude: 38.9446, longitude: -92.3266 }, // Mock location
    setUserLocation: (location) => set({ userLocation: location }),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

    layerVisibility: {
        routes: true,
        incidents: true,
        phones: true,
        patrolZones: true,
    },
    toggleLayer: (layer) => set((state) => ({
        layerVisibility: {
            ...state.layerVisibility,
            [layer]: !state.layerVisibility[layer]
        }
    })),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
}));

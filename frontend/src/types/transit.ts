export interface TransitStop {
    id: number;
    route_id: number;
    stop_code: string;
    stop_name: string;
    stop_sequence: number;
    latitude: number;
    longitude: number;
    route_name?: string;
    route_color?: string;
    is_timepoint?: boolean;
}

export interface ScheduleEntry {
    departure_time: string; // "HH:MM:SS"
    service_type: 'weekday' | 'saturday' | 'sunday';
    is_last_stop: boolean;
    stop_id: number;
    stop_code: string;
    stop_name: string;
}

export interface NextBusInfo {
    next_arrival: string | null; // "HH:MM"
    minutes_until: number | null;
    upcoming_times: string[]; // Next 3-4 times
}

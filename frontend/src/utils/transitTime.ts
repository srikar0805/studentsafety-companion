import type { ScheduleEntry, NextBusInfo } from '../types/transit';

/**
 * Calculate next bus arrival time based on current time and schedule
 */
export function calculateNextBus(
    schedules: ScheduleEntry[],
    currentTime: Date = new Date()
): NextBusInfo {
    const now = currentTime;
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    const dayOfWeek = now.getDay(); // 0=Sunday, 6=Saturday

    // Determine service type based on day of week
    let serviceType: 'weekday' | 'saturday' | 'sunday' = 'weekday';
    if (dayOfWeek === 0) serviceType = 'sunday';
    else if (dayOfWeek === 6) serviceType = 'saturday';

    // Filter schedules for today's service type and non-last stops
    const todaySchedules = schedules
        .filter(s => s.service_type === serviceType && !s.is_last_stop)
        .map(s => {
            const [hours, mins] = s.departure_time.split(':').map(Number);
            return {
                time: s.departure_time,
                minutes: hours * 60 + mins
            };
        })
        .sort((a, b) => a.minutes - b.minutes);

    // Remove duplicates
    const uniqueSchedules = todaySchedules.filter((schedule, index, self) =>
        index === self.findIndex((s) => s.minutes === schedule.minutes)
    );

    // Find upcoming buses
    const upcoming = uniqueSchedules.filter(s => s.minutes >= currentMinutes);

    if (upcoming.length === 0) {
        return {
            next_arrival: null,
            minutes_until: null,
            upcoming_times: []
        };
    }

    const nextBus = upcoming[0];
    const minutesUntil = nextBus.minutes - currentMinutes;

    return {
        next_arrival: nextBus.time.substring(0, 5), // "HH:MM"
        minutes_until: minutesUntil,
        upcoming_times: upcoming.slice(0, 4).map(u => u.time.substring(0, 5))
    };
}

/**
 * Format time from 24-hour to 12-hour format
 */
export function formatTime12Hour(time24: string): string {
    const [hours, minutes] = time24.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;
    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
}

import {CalendarDate} from "../interfaces/common";

export function formatCalendarDate(date: CalendarDate): string {
    const getLabel = (d: Date | null): string => {
        if (!d) return '-';

        const today = new Date();
        const tomorrow = new Date();
        tomorrow.setDate(today.getDate() + 1);

        const isSameDay = (d1: Date, d2: Date): boolean =>
            d1.getDate() === d2.getDate() &&
            d1.getMonth() === d2.getMonth() &&
            d1.getFullYear() === d2.getFullYear();

        const pad = (n: number): string => n.toString().padStart(2, '0');
        const day = pad(d.getDate());
        const month = pad(d.getMonth() + 1);

        if (isSameDay(d, today)) return `Today, ${day}.${month}`;
        if (isSameDay(d, tomorrow)) return `Tomorrow, ${day}.${month}`;
        return `${day}.${month}`;
    };

    if (Array.isArray(date)) {
        return `${getLabel(date[0])} - ${getLabel(date[1])}`;
    }

    return getLabel(date);
}

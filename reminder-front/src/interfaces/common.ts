export interface IDevice {
    model: string;
    serial_number: string;
    secret: string;
    id?: number;
}

export interface IReminder {
    time_: string;
    date_: string;
    message_: string
    id?: string;
}

export interface AxiosError {
    message: string;
    name: string;
    stack: string;
    config: any;
    code: string;
    status: number;
}

export type CalendarDatePiece = Date | null;

export type CalendarDate = CalendarDatePiece | [CalendarDatePiece, CalendarDatePiece];
import $api from "../http";
import {IReminder} from "../interfaces/common";



export default class ReminderService {
    static async getReminders(): Promise<IReminder[]> {
        return $api.get<IReminder[]>('/reminders').then(response => response.data);
    }

    static async getRemindersByDate(date: string): Promise<IReminder[]> {
        return $api.get<IReminder[]>(`/reminders/by-date?date_=${date}`).then(response => response.data);
    }

    static async addReminder(reminder: IReminder) {
        return $api.post(
            `/reminders`,
            {
                time_: reminder.time_,
                date_: reminder.date_,
                message_: reminder.message_
            })

    }

    static async deleteReminder(reminderId: string) {
        return $api.delete(`/reminders/${reminderId}`)
    }

    static async deleteExpiredReminders() {
        return $api.delete(`/reminders/expired`)
    }

}

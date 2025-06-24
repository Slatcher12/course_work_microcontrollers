from pydantic import BaseModel
from datetime import time, date


class ReminderBase(BaseModel):
    time_: time
    date_: date
    message_: str


class CreateReminder(ReminderBase):
    pass


class Reminder(ReminderBase):
    id: int

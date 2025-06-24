from typing import List

from fastapi import APIRouter, Depends, Path, Query

from schemas.reminder import CreateReminder, Reminder
from schemas.common import MessageResponse
from controllers.auth import get_current_user
from controllers.reminder import RemindersCtrl
from controllers.devices import get_device
from models.user import User
from models.device import Device
from datetime import date



reminders_router = APIRouter(tags=["Reminders"])


@reminders_router.post(path="/")
async def add_reminder(
        create_reminder: CreateReminder,
        user: User = Depends(get_current_user),
        reminders_ctrl: RemindersCtrl = Depends()
) -> Reminder:
    response = await reminders_ctrl.create(
        user.id,
        create_reminder.date_,
        create_reminder.time_,
        create_reminder.message_
    )
    return response


@reminders_router.get(path="/")
async def get_reminders(
        user: User = Depends(get_current_user),
        reminders_ctrl: RemindersCtrl = Depends()
) -> List[Reminder]:
    response = await reminders_ctrl.get_all(user.id)
    return response

@reminders_router.get(path="/by-date")
async def get_reminders_by_date(
        date_: date = Query(..., description="Дата для фільтрації"),
        user: User = Depends(get_current_user),
        reminders_ctrl: RemindersCtrl = Depends()
) -> List[Reminder]:
    reminders = await reminders_ctrl.get_by_date(user.id, date_)
    return reminders


@reminders_router.get(path="/as-device")
async def get_reminders(
        device: Device = Depends(get_device),
        reminders_ctrl: RemindersCtrl = Depends()
) -> List[Reminder]:
    response = await reminders_ctrl.get_all_as_device(device.id)
    return response

@reminders_router.delete("/expired")
async def delete_expired_alarms(
    reminders_ctrl: RemindersCtrl = Depends()
) -> MessageResponse:
    count = await reminders_ctrl.delete_expired()
    return MessageResponse(message=f"Deleted {count} expired alarms")

@reminders_router.delete(path="/{reminder_id}")
async def get_reminders(
        reminder_id: int = Path(),
        user: User = Depends(get_current_user),
        reminders_ctrl: RemindersCtrl = Depends()
) -> MessageResponse:
    await reminders_ctrl.delete(reminder_id)
    return MessageResponse(message="Alarm clock deleted successfully")



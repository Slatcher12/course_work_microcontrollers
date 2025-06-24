from typing import List
from datetime import date, time
from datetime import datetime


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from controllers.base import BaseController
from database.session import get_session
from repositories.reminder import RemindersRepo
from models.reminder import Reminder


class RemindersCtrl(BaseController):

    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session)
        self.repo = RemindersRepo(session)

    async def create(self, user_id: int, date_: date, time_: time, message_: str) -> Reminder:
        reminder = await self.repo.create(
            {
                "user_id": user_id,
                "date_": date_,
                "time_": time_,
                "message_": message_
            }
        )
        await self.session.commit()
        return reminder

    async def get_all(self, user_id: int):
        reminders = await self.repo.get_by("user_id", user_id)
        return reminders

    async def get_all_as_device(self, device_id):
        reminders = await self.repo.get_by_device_id(device_id)
        return reminders

    async def delete(self, reminder_id: int):
        reminder = await self.repo.get_by("id", reminder_id, unique=True)
        if not reminder:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Reminder not found")
        await self.repo.delete(reminder)
        await self.session.commit()

    async def get_by_date(self, user_id: int, date_: date):
        reminders = await self.repo.get_by_multiple({"user_id": user_id, "date_": date_})
        return reminders
    
    async def delete_expired(self):
        now = datetime.now()
        count = await self.repo.delete_expired(now.date(), now.time())
        return count



from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, time

from repositories.base import BaseRepository
from models.reminder import Reminder
from models.user import User
from models.device import Device


class RemindersRepo(BaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Reminder)

    async def get_by_device_id(self, device_id):
        query = self.query()
        query = query.join(User).join(Device).where(Device.id == device_id)
        return await self.all(query)
    
    async def get_by_multiple(self, filters: dict):
        query = self.query()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return await self.all(query)
    
    async def delete_expired(self, current_date: date, current_time: time):
        query = self.query().where(
            (self.model.date_ < current_date) |
            ((self.model.date_ == current_date) & (self.model.time_ < current_time))
        )
        expired_reminders = await self.all(query)
        for reminder in expired_reminders:
            await self.delete(reminder)
        await self.session.commit()
        return len(expired_reminders)

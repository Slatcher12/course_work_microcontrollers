from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import BaseRepository
from models.device import Device


class DevicesRepo(BaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Device)

    async def get_by_serial(self, device_serial: str, device_secret: str) -> Device:
        query = self.query()
        query = query.where((Device.serial_number==device_serial) & (Device.secret == device_secret))
        return await self.one(query)

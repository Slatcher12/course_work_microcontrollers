from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Header

from controllers.base import BaseController
from database.session import get_session
from repositories.devices import DevicesRepo
from models.device import Device

from fastapi.security import APIKeyHeader
from fastapi import Security


api_key_header = APIKeyHeader(name="X-DEVICE-TOKEN", scheme_name="deviceToken", auto_error=False)


async def get_device(
        device_token: str = Security(api_key_header),
        session: AsyncSession = Depends(get_session)
) -> Device:
    device_serial, device_secret = device_token.split(":", maxsplit=1)
    repo = DevicesRepo(session)
    device = await repo.get_by_serial(device_serial, device_secret)
    if not device:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")
    return device


class DevicesController(BaseController):

    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session)
        self.repo = DevicesRepo(session)

    async def create_device(self, model: str, serial_number: str, secret: str) -> Device:
        device = await self.repo.create({
            "model": model,
            "serial_number": serial_number,
            "secret": secret
        })
        await self.session.commit()
        return device

    async def get_devices(self) -> List[Device]:
        devices = await self.repo.get_all()
        return devices

    async def delete_device(self, device_id: int) -> None:
        device = await self.repo.get_by("id", device_id, unique=True)
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        await self.repo.delete(device)
        await self.session.commit()

    async def bind_user_to_device(self, user_id: int, device_id: int) -> None:
        device = await self.repo.get_by("id", device_id, unique=True)
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        device.user_id = user_id
        await self.session.commit()

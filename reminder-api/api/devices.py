from typing import List

from fastapi import APIRouter, status, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi import Response

from schemas.devices import (
    Device,
    CreateDevice
)
from controllers.auth import get_admin, get_current_user
from controllers.devices import DevicesController, get_device
from models.user import User as UserModel

from schemas.common import MessageResponse
from schemas.users import CreateUser, User


devices_router = APIRouter(tags=["Devices"])


@devices_router.post("/")
async def add_device(
        create_device: CreateDevice,
        admin: User = Depends(get_admin),
        devices_ctrl: DevicesController = Depends()
) -> Device:
    response = await devices_ctrl.create_device(
        create_device.model,
        create_device.serial_number,
        create_device.secret
    )
    return response


@devices_router.get("/")
async def get_devices(
        admin: User = Depends(get_admin),
        devices_ctrl: DevicesController = Depends()
) -> List[Device]:
    response = await devices_ctrl.get_devices()
    return response


@devices_router.delete("/{device_id}")
async def delete_device(
        device_id: int = Path(),
        admin: User = Depends(get_admin),
        devices_ctrl: DevicesController = Depends()
) -> MessageResponse:
    response = await devices_ctrl.delete_device(device_id)
    return MessageResponse(message="Device deleted successfully")


@devices_router.post("/user")
async def bind_user(
        device: Device = Depends(get_device),
        user: User = Depends(get_current_user),
        devices_ctrl: DevicesController = Depends()
) -> MessageResponse:
    await devices_ctrl.bind_user_to_device(user.id, device.id)
    return MessageResponse(message="Device binded successfully")

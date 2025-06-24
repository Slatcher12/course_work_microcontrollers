from fastapi import APIRouter

from api.auth import auth_router
from api.devices import devices_router
from api.reminder import reminders_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(devices_router, prefix="/devices")
router.include_router(reminders_router, prefix="/reminders")
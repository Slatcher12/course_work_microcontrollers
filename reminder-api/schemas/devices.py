from pydantic import BaseModel


class DeviceBase(BaseModel):
    model: str
    serial_number: str
    secret: str


class CreateDevice(DeviceBase):
    pass


class Device(DeviceBase):
    id: int

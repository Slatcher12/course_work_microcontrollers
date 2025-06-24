from sqlalchemy import (
    String,
    Integer, Column, ForeignKey
)
from sqlalchemy.orm import relationship

from database.base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String, nullable=False)
    serial_number = Column(String, nullable=False)
    secret = Column(String, nullable=False)

    user_id = Column(ForeignKey("users.id"))
    user = relationship("User", back_populates="devices")

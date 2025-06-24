from sqlalchemy import Column
from sqlalchemy import (
    Integer,
    String,
    Enum as SAEnum
)
from enum import Enum

from sqlalchemy.orm import relationship

from database.base import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.ADMIN)

    devices = relationship("Device", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")

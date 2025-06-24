from sqlalchemy import (
    String,
    Integer, Column, ForeignKey, Time, Date
)
from sqlalchemy.orm import relationship

from database.base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_ = Column(Time, nullable=False)
    date_ = Column(Date, nullable=False)
    message_ = Column(String, nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="reminders")
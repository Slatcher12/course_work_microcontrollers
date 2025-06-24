from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr
from typing import Optional
from uuid import UUID

from models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(
        description="Email address of user",
        examples=["john.doe@gmail.com"]
    )
    first_name: Optional[str] = Field(
        description="Name",
        examples=["John"],
        default=None
    )
    last_name: str = Field(
        description="Surname",
        examples=["Doe"]
    )

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    role: UserRole


class CreateUser(UserBase):
    password: str = Field(
        description="Password of user. Warning: it can be seen only once!",
        examples=["Pass123!"]
    )


class ChangePassword(BaseModel):
    new_password: str = Field(
        description="New password"
    )

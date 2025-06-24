from typing import Dict
from typing import Tuple
from typing import Any

from fastapi import (
    Cookie,
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.base import BaseController
from database.session import get_session
from models.user import (
    User,
    UserRole
)
from repositories.users import UsersRepo
from utils.jwthandler import (
    JWTHandler,
    TokenType
)
from utils.passwordhandler import PasswordHandler


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/token",
    auto_error=False
)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
) -> User:
    payload = JWTHandler.decode(token)
    token_type = payload.get("typ")
    if token_type != TokenType.ACCESS:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    user_id: str = payload.get("sub")
    if user_id is None or not user_id.isdigit():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    repo = UsersRepo(session)
    user = await repo.get(user_id=int(user_id))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return user


async def get_admin(
        user: User = Depends(get_current_user)
) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user


async def get_user_by_refresh(
        refresh_token: str = Cookie(
            None, description="HttpOnly cookie refresh token. Set empty if using SwaggerUI"
        ),
        session: AsyncSession = Depends(get_session)
) -> User:
    payload = JWTHandler.decode(refresh_token)
    token_type = payload.get("typ")
    if token_type != TokenType.REFRESH:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    user_id: str = payload.get("sub")
    if user_id is None or not user_id.isdigit():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repo = UsersRepo(session)
    user = await repo.get(user_id=int(user_id))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


class AuthCtrl(BaseController):

    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session)
        self.repo = UsersRepo(session)

    async def register(
            self,
            email: str,
            first_name: str,
            last_name: str,
            password: str
    ) -> User:
        user = await self.repo.get_by(
            "email",
            email,
            unique=True
        )
        if user:
            raise HTTPException(status.HTTP_409_CONFLICT, "User already exists")
        password_hash = PasswordHandler.hash(password)
        user = await self.repo.create(
            attributes={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password_hash": password_hash
            }
        )
        await self.session.commit()
        return user

    async def token(
            self,
            email: str,
            password: str
    ) -> Tuple[Dict[str, Any], str]:
        user: User = await self.repo.get_by(
            "email",
            email,
            unique=True
        )
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong credentials")
        if not PasswordHandler.verify(user.password_hash, password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong credentials")
        refresh_token = JWTHandler.encode(sub=str(user.id), typ=TokenType.REFRESH)
        access_token = JWTHandler.encode(sub=str(user.id), typ=TokenType.ACCESS)
        return {"access_token": access_token, "token_type": "bearer"}, refresh_token

    async def refresh(
            self,
            user_id: int
    ) -> Dict[str, Any]:
        user: User = await self.repo.get_by(
            "user_id",
            user_id,
            unique=True
        )
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong credentials")
        access_token = JWTHandler.encode(sub=str(user.id), typ=TokenType.ACCESS)
        return {"access_token": access_token, "token_type": "bearer"}


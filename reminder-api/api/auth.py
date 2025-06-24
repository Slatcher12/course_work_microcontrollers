from fastapi import APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi import Response

from schemas.auth import Token
from controllers.auth import AuthCtrl, get_user_by_refresh
from models.user import User as UserModel

from utils.jwthandler import JWTHandler
from schemas.common import MessageResponse
from schemas.users import CreateUser, User


auth_router = APIRouter(tags=["Auth"])


@auth_router.post("/register")
async def register(
        create_user: CreateUser,
        auth_ctrl: AuthCtrl = Depends()
) -> User:
    response = await auth_ctrl.register(
        create_user.email,
        create_user.first_name,
        create_user.last_name,
        create_user.password,
    )
    return response


@auth_router.post(
    path="/token",
    description="OAuth2 compatible token generation. Used for logging user in",
)
async def token(
        fa_response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_ctrl: AuthCtrl = Depends()
) -> Token:
    response, refresh_token = await auth_ctrl.token(
        email=form_data.username,
        password=form_data.password
    )
    fa_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=int(JWTHandler.expire_refresh.total_seconds()),
        secure=True,
        samesite='none',
    )
    return Token(**response)


@auth_router.get(
    path="/refresh",
    description="OAuth2 refresh token",
)
async def refresh(
        auth_ctrl: AuthCtrl = Depends(),
        user: UserModel = Depends(get_user_by_refresh)
) -> Token:
    response = await auth_ctrl.refresh(
        user_id=user.user_id
    )
    return Token(**response)


@auth_router.post(
    path="/logout",
    description="Logout (deletes refresh token cookie)"
)
async def logout(
        fa_response: Response,
) -> MessageResponse:
    fa_response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite='none'
    )
    return MessageResponse(message="Log out successfully")




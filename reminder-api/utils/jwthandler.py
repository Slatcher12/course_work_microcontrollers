from datetime import datetime, timedelta
from fastapi import HTTPException, status
from utils.config import config
from pytz import utc
from enum import Enum
from jwt import (
    decode,
    encode,
    ExpiredSignatureError,
    InvalidTokenError
)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class JWTHandler:
    secret_key = config.SECRET_KEY
    algorithm = "HS256"
    expire_access = timedelta(minutes=50)
    expire_refresh = timedelta(days=14)

    @staticmethod
    def encode(sub: str, typ: TokenType) -> str:
        if typ == TokenType.ACCESS:
            exp = datetime.now(tz=utc) + JWTHandler.expire_access
        elif typ == TokenType.REFRESH:
            exp = datetime.now(tz=utc) + JWTHandler.expire_refresh
        else:
            raise ValueError("Invalid token type specified")
        payload = {
            "exp": exp,
            "sub": sub,
            "typ": typ.value,
        }
        return encode(
            payload, JWTHandler.secret_key, algorithm=JWTHandler.algorithm
        )

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return decode(
                token, JWTHandler.secret_key, algorithms=[JWTHandler.algorithm]
            )
        except ExpiredSignatureError as exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "TokenExpired") from exception
        except InvalidTokenError as exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exception

    @staticmethod
    def decode_expired(token: str) -> dict:
        try:
            return decode(
                token,
                JWTHandler.secret_key,
                algorithms=[JWTHandler.algorithm],
                options={"verify_exp": False},
            )
        except InvalidTokenError as exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "TokenExpired") from exception

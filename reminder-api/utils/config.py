from os import getenv
from typing import Any


class EnvVariableNotFound(Exception):
    pass


class Config:

    def __init__(self):
        self.SECRET_KEY = self.get_var('SECRET_KEY')
        self.POSTGRES_USER = self.get_var("POSTGRES_USER")
        self.POSTGRES_PASSWORD = self.get_var("POSTGRES_PASSWORD")
        self.POSTGRES_HOST = self.get_var("POSTGRES_HOST")
        self.POSTGRES_PORT = self.get_var("POSTGRES_PORT")
        self.POSTGRES_DB = self.get_var("POSTGRES_DB")
        self.ALLOW_ORIGINS = self.get_var("ALLOW_ORIGINS").split(",")

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @staticmethod
    def get_var(item: str, optional: bool = False, default: Any = None):
        var = getenv(item)
        if not var and not optional and not default:
            raise EnvVariableNotFound(f"Environment variable {item} not found")
        if not var and default:
            return default
        return var


config = Config()

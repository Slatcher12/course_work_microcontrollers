from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


import asyncio
from database.session import Session, engine
from database.base import Base
import models  # Make sure all models are imported so metadata is complete


from api import router
from utils.config import config


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router, prefix="/api")


def init_middlewares(app_: FastAPI) -> None:
    app_.add_middleware(
        CORSMiddleware,
        **{
            "allow_origins": config.ALLOW_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }
    )


async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def on_startup():
    await init_tables()


async def on_shutdown():
    pass


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await on_startup()
    yield
    await on_shutdown()


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Kola Alarm API",
        lifespan=lifespan
    )
    init_routers(app_)
    init_middlewares(app_)
    return app_


app = create_app()

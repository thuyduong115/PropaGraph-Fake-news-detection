"""FastAPI app: CORS, mount routers, nạp artifacts trong lifespan."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import admin, auth, graphs, health, models, predict, results
from app.core.auth import Authenticator
from app.core.config import Settings, get_settings
from app.core.registry import Registry


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.registry = Registry.load(settings.artifacts_path)
        yield

    app = FastAPI(title="PropaGraph API", version=__version__, lifespan=lifespan)
    app.state.settings = settings
    app.state.auth = Authenticator(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    for module in (health, auth, models, graphs, predict, results, admin):
        app.include_router(module.router, prefix="/api")
    return app


app = create_app()

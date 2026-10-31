"""Punto de entrada FastAPI (el Dockerfile ejecuta `uvicorn app.main:app`)."""
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from app.config import get_settings
from app.database import Base, engine
from app.errors import register_error_handlers
from app.routers import students

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Para el taller basta create_all; en producción usar migraciones (Alembic).
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="API de Estudiantes",
        version=settings.version_label,
        lifespan=lifespan,
    )
    register_error_handlers(application)
    application.include_router(students.router)

    @application.get("/health", tags=["ops"])
    def health() -> dict[str, str]:
        """Health check de Elastic Beanstalk y evidencia de la versión desplegada."""
        return {"status": "ok", "version": settings.version_label, "env": settings.app_env}

    @application.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {"servicio": "API de Estudiantes", "version": settings.version_label, "docs": "/docs"}

    @application.middleware("http")
    async def security_headers(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        return response

    return application


app = create_app()

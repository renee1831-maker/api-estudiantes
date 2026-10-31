"""Errores de dominio y su traducción a HTTP."""
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class DomainError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class StudentNotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, student_id: int) -> None:
        super().__init__(f"Estudiante {student_id} no encontrado.")


class DuplicateEmailError(DomainError):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, correo: str) -> None:
        super().__init__(f"Ya existe un estudiante con el correo {correo}.")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
        # La traza queda en los logs (CloudWatch/Beanstalk), nunca en la respuesta.
        logger.exception("Error no controlado: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})

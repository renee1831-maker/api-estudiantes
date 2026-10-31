"""Configuración por variables de entorno (12-factor)."""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_url: str
    app_version: str
    commit_sha: str
    app_env: str

    @property
    def version_label(self) -> str:
        return f"{self.app_version}+{self.commit_sha[:7]}" if self.commit_sha else self.app_version


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/estudiantes.db"),
        # Cambia APP_VERSION aquí o en el Dockerfile para demostrar un nuevo despliegue.
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        commit_sha=os.getenv("COMMIT_SHA", ""),
        app_env=os.getenv("APP_ENV", "development"),
    )

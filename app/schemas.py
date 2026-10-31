"""DTOs de entrada/salida con validación (Pydantic v2)."""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]


class StudentBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Name
    apellido: Name
    correo: EmailStr

    @field_validator("correo")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Name | None = None
    apellido: Name | None = None
    correo: EmailStr | None = None

    @field_validator("correo")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if value else value


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    correo: str
    creado_en: datetime

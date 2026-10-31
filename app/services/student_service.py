"""Reglas de negocio de estudiantes."""
from sqlalchemy.exc import IntegrityError

from app.errors import DuplicateEmailError, StudentNotFoundError
from app.models import Student
from app.repositories.student_repository import StudentRepository
from app.schemas import StudentCreate, StudentUpdate


class StudentService:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    def list(self, skip: int, limit: int) -> tuple[list[Student], int]:
        return self._repo.list(skip, limit), self._repo.count()

    def get(self, student_id: int) -> Student:
        student = self._repo.get(student_id)
        if student is None:
            raise StudentNotFoundError(student_id)
        return student

    def create(self, data: StudentCreate) -> Student:
        if self._repo.get_by_email(data.correo):
            raise DuplicateEmailError(data.correo)
        try:
            return self._repo.add(Student(**data.model_dump()))
        except IntegrityError:  # carrera entre dos peticiones con el mismo correo
            self._repo.rollback()
            raise DuplicateEmailError(data.correo) from None

    def update(self, student_id: int, data: StudentUpdate) -> Student:
        student = self.get(student_id)
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        new_email = changes.get("correo")
        if new_email and new_email != student.correo and self._repo.get_by_email(new_email):
            raise DuplicateEmailError(new_email)
        for field, value in changes.items():
            setattr(student, field, value)
        try:
            return self._repo.save(student)
        except IntegrityError:
            self._repo.rollback()
            raise DuplicateEmailError(str(new_email)) from None

    def delete(self, student_id: int) -> None:
        self._repo.delete(self.get(student_id))

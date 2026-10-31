"""Acceso a datos. El servicio no conoce SQL ni el motor de base de datos."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Student


class StudentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, skip: int, limit: int) -> list[Student]:
        stmt = select(Student).order_by(Student.id).offset(skip).limit(limit)
        return list(self._db.scalars(stmt))

    def count(self) -> int:
        return int(self._db.scalar(select(func.count()).select_from(Student)) or 0)

    def get(self, student_id: int) -> Student | None:
        return self._db.get(Student, student_id)

    def get_by_email(self, correo: str) -> Student | None:
        return self._db.scalar(select(Student).where(Student.correo == correo))

    def add(self, student: Student) -> Student:
        self._db.add(student)
        self._db.commit()
        self._db.refresh(student)
        return student

    def save(self, student: Student) -> Student:
        self._db.commit()
        self._db.refresh(student)
        return student

    def delete(self, student: Student) -> None:
        self._db.delete(student)
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

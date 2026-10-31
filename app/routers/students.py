"""Controlador REST /students."""
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.student_repository import StudentRepository
from app.schemas import StudentCreate, StudentRead, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> StudentService:
    return StudentService(StudentRepository(db))


ServiceDep = Annotated[StudentService, Depends(get_service)]
StudentId = Annotated[int, Path(gt=0, description="ID del estudiante")]


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, service: ServiceDep) -> StudentRead:
    return StudentRead.model_validate(service.create(data))


@router.get("", response_model=list[StudentRead])
def list_students(
    service: ServiceDep,
    response: Response,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[StudentRead]:
    # Se mantiene la respuesta como lista (compatible con la actividad #4); el total va en cabecera.
    items, total = service.list(skip, limit)
    response.headers["X-Total-Count"] = str(total)
    return [StudentRead.model_validate(s) for s in items]


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: StudentId, service: ServiceDep) -> StudentRead:
    return StudentRead.model_validate(service.get(student_id))


@router.put("/{student_id}", response_model=StudentRead)
def update_student(student_id: StudentId, data: StudentUpdate, service: ServiceDep) -> StudentRead:
    return StudentRead.model_validate(service.update(student_id, data))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: StudentId, service: ServiceDep) -> Response:
    service.delete(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

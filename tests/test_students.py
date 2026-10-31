import pytest
from fastapi.testclient import TestClient

from tests.conftest import ANA


def create(client: TestClient, **overrides: str) -> dict:
    res = client.post("/students", json={**ANA, **overrides})
    assert res.status_code == 201, res.text
    return res.json()


def test_health(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_create_student(client: TestClient) -> None:
    body = create(client)
    assert body["id"] == 1
    assert body["correo"] == "ana@uni.edu"


def test_create_normalizes_email_and_names(client: TestClient) -> None:
    body = create(client, nombre="  Ana ", correo="ANA@Uni.EDU")
    assert body["nombre"] == "Ana"
    assert body["correo"] == "ana@uni.edu"


def test_duplicate_email_returns_409(client: TestClient) -> None:
    create(client)
    res = client.post("/students", json={**ANA, "correo": "Ana@uni.edu"})
    assert res.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {**ANA, "correo": "no-es-correo"},
        {**ANA, "nombre": ""},
        {**ANA, "nombre": "x" * 81},
        {"nombre": "Ana", "apellido": "Garcia"},
        {**ANA, "rol": "admin"},
    ],
)
def test_invalid_payload_returns_422(client: TestClient, payload: dict) -> None:
    assert client.post("/students", json=payload).status_code == 422


def test_list_students_with_total_header(client: TestClient) -> None:
    create(client)
    create(client, nombre="Laura", correo="laura@uni.edu")
    res = client.get("/students")
    assert res.status_code == 200
    assert [s["nombre"] for s in res.json()] == ["Ana", "Laura"]
    assert res.headers["X-Total-Count"] == "2"


def test_list_pagination_limits(client: TestClient) -> None:
    assert client.get("/students?limit=0").status_code == 422
    assert client.get("/students?limit=101").status_code == 422


def test_get_student_by_id(client: TestClient) -> None:
    create(client)
    assert client.get("/students/1").json()["nombre"] == "Ana"


def test_get_missing_student_returns_404(client: TestClient) -> None:
    assert client.get("/students/99").status_code == 404


def test_get_invalid_id_returns_422(client: TestClient) -> None:
    assert client.get("/students/0").status_code == 422


def test_update_student(client: TestClient) -> None:
    create(client)
    res = client.put("/students/1", json={"apellido": "Gómez"})
    assert res.status_code == 200
    assert res.json()["apellido"] == "Gómez"


def test_update_to_existing_email_returns_409(client: TestClient) -> None:
    create(client)
    create(client, correo="laura@uni.edu")
    assert client.put("/students/2", json={"correo": "ana@uni.edu"}).status_code == 409


def test_delete_student(client: TestClient) -> None:
    create(client)
    assert client.delete("/students/1").status_code == 204
    assert client.get("/students/1").status_code == 404

import os
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from sqlalchemy import event, func, select
from sqlalchemy.exc import OperationalError

from app.models import AuditLog, Priority, Request, Status, User

PAYLOAD = {
    "title": "  Не работает кабинет  ",
    "description": "Ошибка после входа",
    "category_id": 1,
}


def create(client, headers):
    response = client.post("/api/v1/requests", json=PAYLOAD, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_login_and_swagger(context):
    client, _, _ = context
    assert client.get("/docs").status_code == 200
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "first@susu.ru", "password": "Test-password-123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
    assert client.get("/api/v1/categories", headers=headers).json()[0]["name"] == "ИТ"
    for email, password in [("first@susu.ru", "wrong"), ("missing@susu.ru", "wrong")]:
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": email, "password": password}
            ).status_code
            == 401
        )


def test_create_persists_with_audit_and_deadline(context, headers):
    client, factory, _ = context
    item = create(client, headers)
    assert item["title"] == "Не работает кабинет"
    assert item["status"] == "Новая" and item["priority"] == "Средняя"
    assert item["responsible_id"] is None
    assert datetime.fromisoformat(item["deadline_at"]) - datetime.fromisoformat(
        item["created_at"]
    ) == timedelta(hours=48)
    with factory() as db:
        assert db.get(Request, item["id"]).applicant_id == 1
        assert db.scalar(select(func.count()).select_from(AuditLog)) == 1
    assert client.get(f"/api/v1/requests/{item['id']}", headers=headers).json() == item


@pytest.mark.parametrize(
    "patch",
    [
        {"title": ""},
        {"title": " "},
        {"title": "x" * 201},
        {"description": ""},
        {"description": "x" * 10001},
        {"category_id": 0},
        {"category_id": 999},
        {"applicant_id": 2},
        {"status_id": 2},
        {"priority_id": 1},
        {"responsible_id": 2},
        {"ai_confidence": 1},
    ],
)
def test_invalid_create(context, headers, patch):
    client, factory, _ = context
    assert (
        client.post(
            "/api/v1/requests", json=PAYLOAD | patch, headers=headers
        ).status_code
        == 422
    )
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(Request)) == 0


@pytest.mark.parametrize(
    "path,method",
    [
        ("/categories", "get"),
        ("/requests", "get"),
        ("/requests", "post"),
        ("/requests/1", "get"),
        ("/requests/1", "patch"),
    ],
)
def test_auth_required(context, path, method):
    client, _, _ = context
    kwargs = (
        {"json": PAYLOAD}
        if method == "post"
        else {"json": {"title": "test"}}
        if method == "patch"
        else {}
    )
    assert getattr(client, method)("/api/v1" + path, **kwargs).status_code == 401


@pytest.mark.parametrize(
    "kind", ["tampered", "expired", "missing_exp", "wrong_secret", "unknown_user"]
)
def test_invalid_tokens(context, kind):
    client, _, _ = context
    data = {
        "sub": "1",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    secret = os.environ["SECRET_KEY"]
    if kind == "expired":
        data["exp"] = datetime.now(UTC) - timedelta(minutes=1)
    if kind == "missing_exp":
        data.pop("exp")
    if kind == "unknown_user":
        data["sub"] = "999"
    token = jwt.encode(
        data,
        secret if kind != "wrong_secret" else "different-secret-12345678901234567890",
        algorithm="HS256",
    )
    if kind == "tampered":
        token = "invalid.token.signature"
    assert (
        client.get(
            "/api/v1/requests", headers={"Authorization": "Bearer " + token}
        ).status_code
        == 401
    )


def test_inactive_and_legacy_user(context, headers):
    client, factory, _ = context
    with factory() as db:
        db.get(User, 1).is_active = False
        db.get(User, 2).password_hash = "demo_hash_002"
        db.commit()
    assert client.get("/api/v1/requests", headers=headers).status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "first@susu.ru", "password": "Test-password-123"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "second@susu.ru", "password": "demo_hash_002"},
        ).status_code
        == 401
    )


def test_owner_isolation_and_pagination(context, headers):
    client, _, _ = context
    item = create(client, headers)
    from app.security import create_token

    other = {"Authorization": "Bearer " + create_token(2)}
    assert client.get("/api/v1/requests", headers=other).json()["total"] == 0
    assert (
        client.get(f"/api/v1/requests/{item['id']}", headers=other).status_code == 404
    )
    assert (
        client.patch(
            f"/api/v1/requests/{item['id']}", json={"title": "change"}, headers=other
        ).status_code
        == 404
    )
    create(client, headers)
    page = client.get("/api/v1/requests?limit=1&offset=1", headers=headers).json()
    assert page["total"] == 2 and page["items"][0]["id"] == item["id"]
    assert client.get("/api/v1/requests?limit=0", headers=headers).status_code == 422
    assert client.get("/api/v1/requests?limit=101", headers=headers).status_code == 422
    assert client.get("/api/v1/requests?offset=-1", headers=headers).status_code == 422


def test_update_new_only(context, headers):
    client, factory, _ = context
    item = create(client, headers)
    url = f"/api/v1/requests/{item['id']}"
    assert (
        client.patch(
            url, json={"title": "Исправленный заголовок"}, headers=headers
        ).json()["title"]
        == "Исправленный заголовок"
    )
    for payload in [
        {},
        {"title": None},
        {"title": " "},
        {"status_id": 2},
        {"category_id": 1},
    ]:
        assert client.patch(url, json=payload, headers=headers).status_code == 422
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(AuditLog)) == 2
        db.get(Request, item["id"]).status_id = 2
        db.commit()
    assert (
        client.patch(url, json={"title": "change"}, headers=headers).status_code == 409
    )
    assert client.get("/api/v1/requests/999", headers=headers).status_code == 404


@pytest.mark.parametrize("missing", [Status, Priority])
def test_missing_defaults(context, headers, missing):
    client, factory, _ = context
    with factory() as db:
        db.delete(db.get(missing, 1))
        db.commit()
    assert (
        client.post("/api/v1/requests", json=PAYLOAD, headers=headers).status_code
        == 503
    )


def test_audit_failure_rolls_back_request(context, headers):
    client, factory, engine = context

    def fail_audit(conn, cursor, statement, params, execution_context, executemany):
        if statement.startswith("INSERT INTO audit_log"):
            raise OperationalError(statement, params, Exception("simulated DB failure"))

    event.listen(engine, "before_cursor_execute", fail_audit)
    try:
        response = client.post("/api/v1/requests", json=PAYLOAD, headers=headers)
        assert response.status_code == 503
        assert "simulated" not in response.text
    finally:
        event.remove(engine, "before_cursor_execute", fail_audit)
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(Request)) == 0
        assert db.scalar(select(func.count()).select_from(AuditLog)) == 0
    create(client, headers)

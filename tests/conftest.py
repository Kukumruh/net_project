import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-only-12345678901234567890")
from app.database import Base, get_db
from app.main import app
from app.models import Category, Priority, Role, Status, User
from app.security import create_token, hash_password


@pytest.fixture
def context():
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    if (
        not url.startswith("sqlite")
        and not os.getenv("ALLOW_TEST_DATABASE_RESET") == "1"
    ):
        raise RuntimeError(
            "Set ALLOW_TEST_DATABASE_RESET=1 only for a disposable test DB"
        )
    engine = create_engine(
        url,
        **(
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
            if url.startswith("sqlite")
            else {}
        ),
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    encoded = hash_password("Test-password-123")
    with factory() as db:
        role = Role(name="Заявитель")
        db.add(role)
        db.flush()
        db.add_all(
            [
                User(
                    full_name="First",
                    email="first@susu.ru",
                    password_hash=encoded,
                    role_id=role.id,
                ),
                User(
                    full_name="Second",
                    email="second@susu.ru",
                    password_hash=encoded,
                    role_id=role.id,
                ),
                Category(name="ИТ"),
                Status(name="Новая", sort_order=1),
                Status(name="В работе", sort_order=2),
                Priority(name="Средняя", sla_hours=48),
            ]
        )
        db.commit()

    def override_db():
        with factory() as db:
            try:
                yield db
            except Exception:
                db.rollback()
                raise

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            yield client, factory, engine
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def headers():
    return {"Authorization": "Bearer " + create_token(1)}

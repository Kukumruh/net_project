import importlib

from sqlalchemy import func, select

from app.models import Request, User
from app.security import hash_password, verify_password


def test_seed_is_repeatable_and_upgrades_only_legacy_passwords(context, monkeypatch):
    _, factory, _ = context
    monkeypatch.setenv("DEMO_PASSWORD", "Explicit-demo-password-123")
    seed = importlib.import_module("seed.seed")
    monkeypatch.setattr(seed, "SessionLocal", factory)
    seed.seed()
    real_hash = hash_password("Private-password-123")
    with factory() as db:
        ivanov = db.scalar(select(User).where(User.email == "ivanov@susu.ru"))
        petrov = db.scalar(select(User).where(User.email == "petrov@susu.ru"))
        assert verify_password("Explicit-demo-password-123", ivanov.password_hash)
        ivanov.password_hash = real_hash
        petrov.password_hash = "demo_hash_002"
        db.commit()
        count = db.scalar(select(func.count()).select_from(Request))
    seed.seed()
    with factory() as db:
        assert (
            db.scalar(select(User).where(User.email == "ivanov@susu.ru")).password_hash
            == real_hash
        )
        assert verify_password(
            "Explicit-demo-password-123",
            db.scalar(select(User).where(User.email == "petrov@susu.ru")).password_hash,
        )
        assert db.scalar(select(func.count()).select_from(Request)) == count


def test_seed_requires_explicit_password(context, monkeypatch):
    _, factory, _ = context
    monkeypatch.delenv("DEMO_PASSWORD", raising=False)
    seed = importlib.import_module("seed.seed")
    monkeypatch.setattr(seed, "SessionLocal", factory)
    import pytest

    with pytest.raises(RuntimeError, match="DEMO_PASSWORD"):
        seed.seed()
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(Request)) == 0

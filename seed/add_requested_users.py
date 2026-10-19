"""Safely add/update the five requested demo accounts without touching other data.

Usage inside the API container:
    INITIAL_USERS_PASSWORD='...' python seed/add_requested_users.py

Only these five email addresses are affected. Existing rows keep their IDs and
all related requests/comments/attachments; only password_hash and role_id are
updated for matching accounts. Names and other profile fields are preserved.
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Role, User
from app.security import hash_password


ACCOUNTS = [
    {
        "email": "ivanov@susu.ru",
        "full_name": "Иванов Иван Иванович",
        "role": "Заявитель",
    },
    {
        "email": "petrov@susu.ru",
        "full_name": "Петров Пётр Сергеевич",
        "role": "Заявитель",
    },
    {
        "email": "operator1@susu.ru",
        "full_name": "Оператор 1",
        "role": "Оператор",
    },
    {
        "email": "operator2@susu.ru",
        "full_name": "Оператор 2",
        "role": "Оператор",
    },
    {
        "email": "admin@susu.ru",
        "full_name": "Администратор",
        "role": "Администратор",
    },
]


def main() -> None:
    password = os.getenv("INITIAL_USERS_PASSWORD", "")
    if len(password) < 12:
        raise SystemExit(
            "Set INITIAL_USERS_PASSWORD to a password of at least 12 characters."
        )

    db = SessionLocal()
    created = []
    updated = []
    try:
        roles = {}
        for role_name in {account["role"] for account in ACCOUNTS}:
            role = db.scalar(select(Role).where(Role.name == role_name))
            if role is None:
                raise RuntimeError(
                    f"Role '{role_name}' is missing. Run the project migrations/seed first."
                )
            roles[role_name] = role

        for account in ACCOUNTS:
            email = account["email"]
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(
                    full_name=account["full_name"],
                    email=email,
                    password_hash=hash_password(password),
                    role_id=roles[account["role"]].id,
                    is_active=True,
                )
                db.add(user)
                created.append(email)
            else:
                # Keep ID, name, activity state, department, Telegram ID, and related records.
                # The requested password and role are deliberately applied to these accounts.
                user.password_hash = hash_password(password)
                user.role_id = roles[account["role"]].id
                updated.append(email)

        db.commit()
        print(f"Created: {len(created)}")
        for email in created:
            print(f"  CREATED {email}")
        print(f"Updated requested accounts: {len(updated)}")
        for email in updated:
            print(f"  UPDATED password/role {email}")
        print("Done. No other users or application data were modified.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import unauthorized
from app.database import get_db
from app.models import User
from app.schemas.request import Login, Token
from app.security import DUMMY_HASH, create_token, verify_password

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/login", response_model=Token)
def login(payload: Login, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    valid = verify_password(
        payload.password, user.password_hash if user else DUMMY_HASH
    )
    if not valid or user is None or not user.is_active:
        raise unauthorized()
    return Token(access_token=create_token(user.id))

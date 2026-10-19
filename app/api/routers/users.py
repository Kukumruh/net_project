from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import current_user
from app.database import get_db
from app.models import Role, User
from app.schemas.users import UserCreate, UserOut
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["Пользователи"])

def require_admin(user: User) -> None:
    if user.role.name != "Администратор":
        raise HTTPException(status_code=403, detail="Управлять пользователями может только администратор")

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current: User = Depends(current_user)):
    require_admin(current)
    users = db.scalars(select(User).order_by(User.full_name, User.id)).all()
    return [UserOut(id=u.id, full_name=u.full_name, email=u.email, role=u.role.name, is_active=u.is_active) for u in users]

@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current: User = Depends(current_user)):
    require_admin(current)
    role = db.scalar(select(Role).where(Role.name == payload.role))
    if role is None:
        raise HTTPException(status_code=422, detail="Выберите существующую роль")
    existing = db.scalar(select(User.id).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    user = User(full_name=payload.full_name, email=payload.email, password_hash=hash_password(payload.password), role_id=role.id, is_active=True)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    return UserOut(id=user.id, full_name=user.full_name, email=user.email, role=user.role.name, is_active=user.is_active)

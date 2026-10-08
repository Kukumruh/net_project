import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import get_secret

bearer = HTTPBearer(auto_error=False)


def unauthorized():
    return HTTPException(
        401, "Требуется авторизация", headers={"WWW-Authenticate": "Bearer"}
    )


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise unauthorized()
    try:
        payload = jwt.decode(
            credentials.credentials,
            get_secret(),
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "iat"]},
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise unauthorized()
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized()
    return user

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import current_user
from app.database import get_db
from app.models import Category, User
from app.schemas.request import (
    CategoryOut,
    RequestCreate,
    RequestOut,
    RequestPage,
    RequestUpdate,
)
from app.services.request_service import RequestService

router = APIRouter(tags=["Заявки"])


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post("/requests", response_model=RequestOut, status_code=201)
def create(
    payload: RequestCreate,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    result = RequestService(db).create(payload, user.id)
    response.headers["Location"] = f"/api/v1/requests/{result.id}"
    return result


@router.get("/requests", response_model=RequestPage)
def listing(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    service = RequestService(db)
    items, total = service.repo.list_owned(user.id, limit, offset)
    return RequestPage(
        items=[service.serialize(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/requests/{request_id}", response_model=RequestOut)
def detail(
    request_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
):
    service = RequestService(db)
    return service.serialize(service.get(request_id, user.id))


@router.patch("/requests/{request_id}", response_model=RequestOut)
def update(
    request_id: int,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return RequestService(db).update(request_id, payload, user.id)

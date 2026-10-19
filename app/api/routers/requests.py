from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import current_user
from app.database import get_db
from app.models import Category, RequestComment, User
from app.schemas.request import (
    CategoryOut,
    RequestCreate,
    RequestOut,
    RequestPage,
    RequestUpdate,
    RequestWorkflowUpdate,
    CommentOut,
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
    if user.role.name in {"Оператор", "Администратор"}:
        items, total = service.repo.list_all(limit, offset)
    else:
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
    if user.role.name in {"Оператор", "Администратор"}:
        return service.serialize(service.get_any(request_id))
    return service.serialize(service.get(request_id, user.id))


@router.patch("/requests/{request_id}", response_model=RequestOut)
def update(
    request_id: int,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return RequestService(db).update(request_id, payload, user.id)


@router.patch("/requests/{request_id}/workflow", response_model=RequestOut)
def workflow_update(
    request_id: int, payload: RequestWorkflowUpdate,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    if user.role.name not in {"Оператор", "Администратор"}:
        raise HTTPException(403, "Изменять статус могут только оператор и администратор")
    if payload.status not in {"Готово", "Отложена", "В работе", "Назначена", "На проверке"}:
        raise HTTPException(422, "Недопустимый статус обработки")
    return RequestService(db).workflow_update(request_id, user, payload.status, payload.explanation)


@router.get("/requests/{request_id}/comments", response_model=list[CommentOut])
def comments(
    request_id: int, db: Session = Depends(get_db), user: User = Depends(current_user),
):
    service = RequestService(db)
    item = service.get_any(request_id) if user.role.name in {"Оператор", "Администратор"} else service.get(request_id, user.id)
    return db.scalars(
        select(RequestComment).where(
            RequestComment.request_id == item.id, RequestComment.is_internal.is_(False)
        ).order_by(RequestComment.created_at.asc(), RequestComment.id.asc())
    ).all()

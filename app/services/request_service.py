from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select

from app.models import AuditLog, Category, Priority, Request, Status
from app.repositories.request_repository import RequestRepository
from app.schemas.request import RequestOut


class RequestService:
    def __init__(self, db):
        self.db = db
        self.repo = RequestRepository(db)

    @staticmethod
    def serialize(item):
        return RequestOut(
            id=item.id,
            title=item.title,
            description=item.description,
            category_id=item.category_id,
            category=item.category.name,
            status=item.status.name,
            priority=item.priority.name,
            responsible_id=item.responsible_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
            deadline_at=item.deadline_at,
        )

    def get(self, request_id, user_id, lock=False):
        item = self.repo.get_owned(request_id, user_id, lock)
        if item is None:
            raise HTTPException(404, "Заявка не найдена")
        return item

    def create(self, payload, user_id):
        category = self.db.get(Category, payload.category_id)
        if category is None:
            raise HTTPException(422, "Категория не существует")
        status = self.db.scalar(select(Status).where(Status.name == "Новая"))
        priority = self.db.scalar(select(Priority).where(Priority.name == "Средняя"))
        if status is None or priority is None or priority.sla_hours <= 0:
            raise HTTPException(503, "Не настроены статус или стандартный приоритет")
        now = datetime.now(UTC).replace(
            tzinfo=None
        )  # Existing DB columns store UTC without timezone.
        item = Request(
            **payload.model_dump(),
            applicant_id=user_id,
            status_id=status.id,
            priority_id=priority.id,
            created_at=now,
            updated_at=now,
            deadline_at=now + timedelta(hours=priority.sla_hours),
        )
        self.db.add(item)
        self.db.flush()
        self.db.add(
            AuditLog(
                user_id=user_id,
                action="request.create",
                entity_type="request",
                entity_id=item.id,
            )
        )
        self.db.commit()
        return self.serialize(self.get(item.id, user_id))

    def update(self, request_id, payload, user_id):
        item = self.get(request_id, user_id, lock=True)
        if item.status.name != "Новая":
            raise HTTPException(409, "Изменять текст можно только у новой заявки")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        item.updated_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.add(
            AuditLog(
                user_id=user_id,
                action="request.update",
                entity_type="request",
                entity_id=item.id,
            )
        )
        self.db.commit()
        return self.serialize(item)

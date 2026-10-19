from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select

from app.models import AuditLog, Category, Priority, Request, Status, RequestComment
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

    @staticmethod
    def classify_priority(title, description):
        """Rule-based triage: impact/urgency phrases map to configured SLA tiers."""
        text = f"{title} {description}".casefold()
        critical = ("авар", "пожар", "угроз", "утечк", "массовый сбой",
                    "полностью недоступ", "вся система не работает", "опасн")
        high = ("срочно", "не работает", "невозможно войти", "заблокирован",
                "не могу войти", "сбой", "не открывается", "не запускается",
                "потерял доступ", "нет доступа")
        low = ("консультац", "предложение", "уточнить", "небольшое улучшение", "вопрос по")
        if any(word in text for word in critical):
            return "Высокая"
        if any(word in text for word in high):
            return "Высокая"
        if any(word in text for word in low):
            return "Низкая"
        return "Средняя"

    def get_any(self, request_id, lock=False):
        item = self.repo.get_any(request_id, lock)
        if item is None:
            raise HTTPException(404, "Заявка не найдена")
        return item

    def workflow_update(self, request_id, user, status_name, explanation):
        item = self.get_any(request_id, lock=True)
        status_aliases = {"Готово": ("Готово", "Решена", "Закрыта"), "Отложена": ("Отложена", "Отклонена")}\n        candidates = status_aliases.get(status_name, (status_name,))\n        status = self.db.scalar(select(Status).where(Status.name.in_(candidates)).order_by(Status.sort_order.desc()).limit(1))
        if status is None:
            # Repair stale dictionaries in existing databases. Older installations may
            # not have statuses introduced after their initial seed.
            max_order = self.db.scalar(select(Status.sort_order).order_by(Status.sort_order.desc()).limit(1))
            status = Status(name=status_name, sort_order=(max_order or 0) + 1)
            self.db.add(status)
            self.db.flush()
        now = datetime.now(UTC).replace(tzinfo=None)
        item.status_id = status.id
        item.updated_at = now
        self.db.add(RequestComment(
            request_id=item.id, author_id=user.id,
            comment_text=explanation.strip(), is_internal=False, created_at=now,
        ))
        self.db.add(AuditLog(
            user_id=user.id, action=f"request.status.{status_name}",
            entity_type="request", entity_id=item.id,
        ))
        self.db.commit()
        return self.serialize(self.get_any(item.id))

    def create(self, payload, user_id):
        category = self.db.get(Category, payload.category_id)
        if category is None:
            raise HTTPException(422, "Категория не существует")
        status = self.db.scalar(select(Status).where(Status.name == "Новая"))
        priority_name = self.classify_priority(payload.title, payload.description)
        priority = self.db.scalar(select(Priority).where(Priority.name == priority_name))
        if priority is None:
            priority = self.db.scalar(select(Priority).where(Priority.name == "Средняя"))
        if status is None or priority is None or priority.sla_hours <= 0:
            raise HTTPException(503, "Не настроены статус или приоритет")
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

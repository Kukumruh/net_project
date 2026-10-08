from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models import Request


class RequestRepository:
    def __init__(self, db):
        self.db = db

    def owned_query(self, user_id):
        return (
            select(Request)
            .where(Request.applicant_id == user_id)
            .options(
                joinedload(Request.category),
                joinedload(Request.status),
                joinedload(Request.priority),
            )
        )

    def get_owned(self, request_id, user_id, lock=False):
        query = self.owned_query(user_id).where(Request.id == request_id)
        if lock:
            # Avoid locking nullable outer-joined relationships in PostgreSQL.
            query = query.with_for_update(of=Request)
        return self.db.scalar(query)

    def list_owned(self, user_id, limit, offset):
        total = self.db.scalar(
            select(func.count())
            .select_from(Request)
            .where(Request.applicant_id == user_id)
        )
        items = self.db.scalars(
            self.owned_query(user_id)
            .order_by(Request.created_at.desc(), Request.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        return items, total

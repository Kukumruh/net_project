from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    priority_id: Mapped[int] = mapped_column(
        ForeignKey("priorities.id"),
        nullable=False
    )

    status_id: Mapped[int] = mapped_column(
        ForeignKey("statuses.id"),
        nullable=False
    )

    responsible_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Уверенность модели в классификации
    ai_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 3),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    deadline_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    applicant = relationship(
        "User",
        foreign_keys=[applicant_id],
        back_populates="requests_created"
    )

    responsible = relationship(
        "User",
        foreign_keys=[responsible_id],
        back_populates="requests_responsible"
    )

    category = relationship(
        "Category",
        back_populates="requests"
    )

    priority = relationship(
        "Priority",
        back_populates="requests"
    )

    status = relationship(
        "Status",
        back_populates="requests"
    )

    comments = relationship(
        "RequestComment",
        back_populates="request"
    )

    attachments = relationship(
        "Attachment",
        back_populates="request"
    )

    notifications = relationship(
        "Notification",
        back_populates="request"
    )
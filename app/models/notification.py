from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[int] = mapped_column(
        ForeignKey("requests.id"),
        nullable=False
    )

    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    telegram_message_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    sent_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    request = relationship(
        "Request",
        back_populates="notifications"
    )

    recipient = relationship(
        "User",
        back_populates="notifications"
    )
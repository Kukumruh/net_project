from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[int] = mapped_column(
        ForeignKey("requests.id"),
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    request = relationship(
        "Request",
        back_populates="attachments"
    )

    uploaded_by_user = relationship(
        "User",
        back_populates="attachments"
    )
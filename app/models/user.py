from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False
    )

    telegram_chat_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True
    )

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    role = relationship("Role", back_populates="users")

    requests_created = relationship(
        "Request",
        foreign_keys="Request.applicant_id",
        back_populates="applicant"
    )

    requests_responsible = relationship(
        "Request",
        foreign_keys="Request.responsible_id",
        back_populates="responsible"
    )

    comments = relationship(
        "RequestComment",
        back_populates="author"
    )

    attachments = relationship(
        "Attachment",
        back_populates="uploaded_by_user"
    )

    assignments = relationship(
        "ResponsibleAssignment",
        back_populates="user"
    )

    notifications = relationship(
        "Notification",
        back_populates="recipient"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )
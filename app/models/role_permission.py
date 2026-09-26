from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False
    )

    action_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    is_allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    role = relationship(
        "Role",
        back_populates="permissions"
    )
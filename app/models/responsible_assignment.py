from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ResponsibleAssignment(Base):
    __tablename__ = "responsible_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="assignments"
    )

    user = relationship(
        "User",
        back_populates="assignments"
    )
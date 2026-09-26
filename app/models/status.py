from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    sort_order: Mapped[int] = mapped_column(
        nullable=False
    )

    requests = relationship(
        "Request",
        back_populates="status"
    )
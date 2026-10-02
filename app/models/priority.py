from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Priority(Base):
    __tablename__ = "priorities"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    # Service Level Agreement hours (нормативное время (в часах)
    # , за которое команда поддержки или исполнитель обязаны решить задачу с данным приоритетом)
    sla_hours: Mapped[int] = mapped_column(
        nullable=False
    )

    requests = relationship(
        "Request",
        back_populates="priority"
    )
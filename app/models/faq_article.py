from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FaqArticle(Base):
    __tablename__ = "faq_articles"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )

    question: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    category = relationship(
        "Category",
        back_populates="faq_articles"
    )
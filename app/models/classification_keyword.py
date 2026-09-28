from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClassificationKeyword(Base):
    __tablename__ = "classification_keywords"

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "keyword_or_example",
            name="uq_category_keyword"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    keyword_or_example: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    category = relationship(
        "Category",
        back_populates="classification_keywords"
    )
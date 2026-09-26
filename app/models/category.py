from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    requests = relationship(
        "Request",
        back_populates="category"
    )

    faq_articles = relationship(
        "FaqArticle",
        back_populates="category"
    )

    assignments = relationship(
        "ResponsibleAssignment",
        back_populates="category"
    )

    classification_keywords = relationship(
        "ClassificationKeyword",
        back_populates="category"
    )
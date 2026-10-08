from datetime import UTC, datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
Description = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)
]


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)
    ]
    password: str = Field(min_length=1, max_length=1024)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title
    description: Description
    category_id: int = Field(gt=0)


class RequestUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title | None = None
    description: Description | None = None

    @model_validator(mode="after")
    def require_changes(self):
        if not self.model_fields_set or any(
            getattr(self, key) is None for key in self.model_fields_set
        ):
            raise ValueError("Передайте хотя бы одно непустое поле")
        return self


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None


class RequestOut(BaseModel):
    id: int
    title: str
    description: str
    category_id: int
    category: str
    status: str
    priority: str
    responsible_id: int | None
    created_at: datetime
    updated_at: datetime
    deadline_at: datetime | None

    @field_validator("created_at", "updated_at", "deadline_at", mode="after")
    @classmethod
    def utc_dates(cls, value):
        return (
            value.replace(tzinfo=UTC)
            if value is not None and value.tzinfo is None
            else value
        )


class RequestPage(BaseModel):
    items: list[RequestOut]
    total: int
    limit: int
    offset: int

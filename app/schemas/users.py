from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
Email = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)]
Password = Annotated[str, StringConstraints(min_length=12, max_length=128)]

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: Name
    email: Email
    password: Password
    role: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

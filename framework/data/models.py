from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Address(BaseModel):
    model_config = ConfigDict(extra="forbid")

    street: str
    city: str
    postal_code: str
    country: str = "US"


class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    address: Address | None = None
    tags: list[str] = Field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

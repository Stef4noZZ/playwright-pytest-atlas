from __future__ import annotations

from typing import Any

from faker import Faker

from framework.data.models import Address, User

_fake = Faker()


def make_address(**overrides: Any) -> Address:
    data: dict[str, Any] = {
        "street": _fake.street_address(),
        "city": _fake.city(),
        "postal_code": _fake.postcode(),
        "country": _fake.country_code(),
    }
    data.update(overrides)
    return Address(**data)


def make_user(**overrides: Any) -> User:
    data: dict[str, Any] = {
        "email": _fake.unique.email(),
        "first_name": _fake.first_name(),
        "last_name": _fake.last_name(),
        "phone": _fake.phone_number(),
    }
    data.update(overrides)
    return User(**data)

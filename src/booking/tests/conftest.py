from decimal import Decimal

import pytest

from booking.models import Room


@pytest.fixture
def room(db):
    return Room.objects.create(
        description="Комната папича с голубыми обоями",
        price=Decimal("1337.00"),
    )
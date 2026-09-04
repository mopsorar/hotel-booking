from datetime import date
from decimal import Decimal

import pytest

from booking.models import Booking, Room


@pytest.mark.django_db
def test_room_can_be_created():
    room = Room.objects.create(
        description="Комната папича с голубыми обоями",
        price=Decimal("1337.00"),
    )

    room_from_db = Room.objects.get(pk=room.pk)

    assert room_from_db.description == "Комната папича с голубыми обоями"
    assert room_from_db.price == Decimal("1337.00")
    assert room_from_db.created_at is not None


def test_booking_can_be_created(room):
    booking = Booking.objects.create(
        room=room,
        date_start=date(2026, 9, 10),
        date_end=date(2026, 9, 15),
    )

    booking_from_db = Booking.objects.get(pk=booking.pk)

    assert booking_from_db.room_id == room.pk
    assert booking_from_db.date_start == date(2026, 9, 10)
    assert booking_from_db.date_end == date(2026, 9, 15)


def test_deleting_room_deletes_its_bookings(room):
    booking = Booking.objects.create(
        room=room,
        date_start=date(2001, 9, 11),
        date_end=date(2001, 9, 12),
    )

    room_id = room.pk
    booking_id = booking.pk

    room.delete()

    assert not Room.objects.filter(pk=room_id).exists()
    assert not Booking.objects.filter(pk=booking_id).exists()

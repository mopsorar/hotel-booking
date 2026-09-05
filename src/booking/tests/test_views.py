from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from booking.models import Booking, Room


def test_create_room(client, db):
    response = client.post(
        reverse("room-create"),
        data={
            "description": "Комната папича с голубыми обоями",
            "price": "1337.00",
        }
    )

    assert response.status_code == 201

    response_data = response.json()
    room = Room.objects.get(pk=response_data["room_id"])

    assert room.description == "Комната папича с голубыми обоями"
    assert room.price == Decimal("1337.00")


def test_create_room_rejects_invalid_price(client, db):
    response = client.post(
        reverse("room-create"),
        data={
            "description": "Комната папича с голубыми обоями",
            "price": "invalid_price",
        }
    )

    assert response.status_code == 400
    assert "price" in response.json()["errors"]
    assert not Room.objects.exists()


def test_list_rooms_sorts_by_price_ascending(client, db):
    expensive_room = Room.objects.create(
        description="Дорогой номер",
        price=Decimal("300.00"),
    )
    cheap_room = Room.objects.create(
        description="Дешевый номер",
        price=Decimal("100.00"),
    )
    middle_room = Room.objects.create(
        description="Средний номер",
        price=Decimal("200.00"),
    )

    response = client.get(
        reverse("room-list"),
        data={
            "sort_by": "price",
            "order": "asc",
        },
    )

    assert response.status_code == 200

    response_data = response.json()
    room_ids = [item["room_id"] for item in response_data]

    assert room_ids == [
        cheap_room.pk,
        middle_room.pk,
        expensive_room.pk,
    ]


def test_list_rooms_sorts_by_price_descending(client, db):
    expensive_room = Room.objects.create(
        description="Дорогой номер",
        price=Decimal("300.00"),
    )
    cheap_room = Room.objects.create(
        description="Дешевый номер",
        price=Decimal("100.00"),
    )
    middle_room = Room.objects.create(
        description="Средний номер",
        price=Decimal("200.00"),
    )

    response = client.get(
        reverse("room-list"),
        data={
            "sort_by": "price",
            "order": "desc",
        },
    )

    assert response.status_code == 200

    response_data = response.json()
    room_ids = [item["room_id"] for item in response_data]

    assert room_ids == [
        expensive_room.pk,
        middle_room.pk,
        cheap_room.pk,
    ]


@pytest.mark.parametrize(
    ("sort_by", "order"),
    [
        ("description", "asc"),
        ("price", "sideways"),
    ],
)
def test_list_rooms_rejects_invalid_sorting(client, sort_by, order):
    response = client.get(
        reverse("room-list"),
        data={
            "sort_by": sort_by,
            "order": order,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "Invalid sorting parameters.",
    }


def test_delete_room_deletes_its_bookings(client, room):
    booking = Booking.objects.create(
        room=room,
        date_start=date(2026, 9, 10),
        date_end=date(2026, 9, 15),
    )
    room_id = room.pk
    booking_id = booking.pk

    response = client.delete(
        reverse(
            "room-delete",
            kwargs={"room_id": room_id},
        )
    )

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert not Room.objects.filter(pk=room_id).exists()
    assert not Booking.objects.filter(pk=booking_id).exists()


def test_delete_nonexistent_room_returns_not_found(client, db):
    response = client.delete(
        reverse(
            "room-delete",
            kwargs={"room_id": 999999},
        )
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Room not found."}


def test_create_booking(client, room):
    response = client.post(
        reverse("booking-create"),
        data={
            "room_id": room.pk,
            "date_start": "2026-09-10",
            "date_end": "2026-09-15",
        },
    )

    assert response.status_code == 201

    response_data = response.json()
    booking = Booking.objects.get(pk=response_data["booking_id"])

    assert booking.room_id == room.pk
    assert booking.date_start == date(2026, 9, 10)
    assert booking.date_end == date(2026, 9, 15)


def test_create_booking_rejects_end_date_before_start_date(client, room):
    response = client.post(
        reverse("booking-create"),
        data={
            "room_id": room.pk,
            "date_start": "2026-09-15",
            "date_end": "2026-09-10",
        },
    )

    assert response.status_code == 400
    assert "date_end" in response.json()["errors"]
    assert not Booking.objects.exists()


def test_list_bookings_filters_by_room_and_sorts_by_start_date(client, room):
    late_booking = Booking.objects.create(
        room=room,
        date_start=date(2026, 9, 20),
        date_end=date(2026, 9, 25),
    )
    early_booking = Booking.objects.create(
        room=room,
        date_start=date(2026, 9, 10),
        date_end=date(2026, 9, 15),
    )

    other_room = Room.objects.create(
        description="Другая комната",
        price=Decimal("500.00"),
    )
    Booking.objects.create(
        room=other_room,
        date_start=date(2026, 9, 5),
        date_end=date(2026, 9, 7),
    )

    response = client.get(
        reverse("booking-list"),
        data={"room_id": room.pk},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "date_start": "2026-09-10",
            "date_end": "2026-09-15",
            "booking_id": early_booking.pk,
        },
        {
            "date_start": "2026-09-20",
            "date_end": "2026-09-25",
            "booking_id": late_booking.pk,
        },
    ]


def test_list_bookings_for_nonexistent_room_returns_not_found(client, db):
    response = client.get(
        reverse("booking-list"),
        data={"room_id": 999999},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Room not found."}


def test_delete_booking_does_not_delete_room(client, room):
    booking = Booking.objects.create(
        room=room,
        date_start=date(2026, 9, 10),
        date_end=date(2026, 9, 15),
    )
    room_id = room.pk
    booking_id = booking.pk

    response = client.delete(
        reverse(
            "booking-delete",
            kwargs={"booking_id": booking_id},
        )
    )

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert not Booking.objects.filter(pk=booking_id).exists()
    assert Room.objects.filter(pk=room_id).exists()


def test_delete_nonexistent_booking_returns_not_found(client, db):
    response = client.delete(
        reverse(
            "booking-delete",
            kwargs={"booking_id": 999999},
        )
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Booking not found."}


@pytest.mark.parametrize(
    ("order", "expected_descriptions"),
    [
        ("asc", ["Старый номер", "Средний номер", "Новый номер"]),
        ("desc", ["Новый номер", "Средний номер", "Старый номер"]),
    ],
)
def test_list_rooms_sorts_by_created_at(
    client,
    db,
    order,
    expected_descriptions,
):
    oldest_room = Room.objects.create(
        description="Старый номер",
        price=Decimal("100.00"),
    )
    middle_room = Room.objects.create(
        description="Средний номер",
        price=Decimal("200.00"),
    )
    newest_room = Room.objects.create(
        description="Новый номер",
        price=Decimal("300.00"),
    )

    Room.objects.filter(pk=oldest_room.pk).update(
        created_at=datetime(2026, 1, 1, tzinfo=UTC)
    )
    Room.objects.filter(pk=middle_room.pk).update(
        created_at=datetime(2026, 2, 1, tzinfo=UTC)
    )
    Room.objects.filter(pk=newest_room.pk).update(
        created_at=datetime(2026, 3, 1, tzinfo=UTC)
    )

    response = client.get(
        reverse("room-list"),
        data={
            "sort_by": "created_at",
            "order": order,
        },
    )

    assert response.status_code == 200

    response_data = response.json()
    descriptions = [item["description"] for item in response_data]

    assert descriptions == expected_descriptions


@pytest.mark.parametrize(
    ("url_name", "url_kwargs", "request_method", "allowed_method"),
    [
        ("room-create", {}, "get", "POST"),
        ("room-list", {}, "post", "GET"),
        ("room-delete", {"room_id": 1}, "get", "DELETE"),
        ("booking-create", {}, "get", "POST"),
        ("booking-list", {}, "post", "GET"),
        ("booking-delete", {"booking_id": 1}, "get", "DELETE"),
    ],
)
def test_endpoints_reject_disallowed_methods(
    client,
    url_name,
    url_kwargs,
    request_method,
    allowed_method,
):
    url = reverse(url_name, kwargs=url_kwargs)
    send_request = getattr(client, request_method)

    response = send_request(url)

    assert response.status_code == 405
    assert response.json() == {"error": "Method not allowed."}
    assert response.headers["Allow"] == allowed_method
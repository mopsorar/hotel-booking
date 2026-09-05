from datetime import date

from booking.forms import BookingCreateForm


def test_booking_create_form_accepts_valid_data(room):
    form = BookingCreateForm(
        data={
            "room_id": room.pk,
            "date_start": "2026-09-10",
            "date_end": "2026-09-15",
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["room_id"] == room
    assert form.cleaned_data["date_start"] == date(2026, 9, 10)
    assert form.cleaned_data["date_end"] == date(2026, 9, 15)


def test_booking_create_form_rejects_invalid_date_format(room):
    form = BookingCreateForm(
        data={
            "room_id": room.pk,
            "date_start": "10.09.2026",
            "date_end": "2026-09-15",
        }
    )

    assert not form.is_valid()
    assert "date_start" in form.errors


def test_booking_create_form_rejects_end_date_before_start_date(room):
    form = BookingCreateForm(
        data={
            "room_id": room.pk,
            "date_start": "2026-09-15",
            "date_end": "2026-09-10",
        }
    )

    assert not form.is_valid()
    assert "date_end" in form.errors


def test_booking_create_form_rejects_nonexistent_room(db):
    form = BookingCreateForm(
        data={
            "room_id": 999999,
            "date_start": "2026-09-10",
            "date_end": "2026-09-15",
        }
    )

    assert not form.is_valid()
    assert "room_id" in form.errors

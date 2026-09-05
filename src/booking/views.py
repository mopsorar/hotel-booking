from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from booking.decorators import require_json_methods
from booking.forms import BookingCreateForm, BookingListForm, RoomCreateForm
from booking.models import Booking, Room


@csrf_exempt
@require_json_methods(["POST"])
def create_room(request):
    form = RoomCreateForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"errors": form.errors.get_json_data()},
            status=400,
        )

    room = form.save()

    return JsonResponse(
        {"room_id": room.id},
        status=201,
    )


@require_json_methods(["GET"])
def list_rooms(request):
    sort_fields = {
        "price": "price",
        "created_at": "created_at",
    }
    sort_directions = {
        "asc": "",
        "desc": "-",
    }

    sort_by = request.GET.get("sort_by", "created_at")
    order = request.GET.get("order", "asc")

    if sort_by not in sort_fields or order not in sort_directions:
        return JsonResponse(
            {"error": "Invalid sorting parameters."},
            status=400,
        )

    ordering = f"{sort_directions[order]}{sort_fields[sort_by]}"
    rooms = Room.objects.order_by(ordering).values(
        "description",
        "price",
        "created_at",
        room_id=F("id"),
    )

    return JsonResponse(list(rooms), safe=False)


@csrf_exempt
@require_json_methods(["DELETE"])
def delete_room(request, room_id):
    deleted_count, _ = Room.objects.filter(id=room_id).delete()

    if deleted_count == 0:
        return JsonResponse(
            {"error": "Room not found."},
            status=404,
        )

    return JsonResponse({"deleted": True})


@csrf_exempt
@require_json_methods(["POST"])
def create_booking(request):
    form = BookingCreateForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"errors": form.errors.get_json_data()},
            status=400,
        )

    booking = Booking.objects.create(
        room=form.cleaned_data["room_id"],
        date_start=form.cleaned_data["date_start"],
        date_end=form.cleaned_data["date_end"],
    )

    return JsonResponse(
        {"booking_id": booking.id},
        status=201,
    )


@require_json_methods(["GET"])
def list_bookings(request):
    form = BookingListForm(request.GET)

    if not form.is_valid():
        return JsonResponse(
            {"errors": form.errors.get_json_data()},
            status=400,
        )

    room_id = form.cleaned_data["room_id"]

    if not Room.objects.filter(id=room_id).exists():
        return JsonResponse(
            {"error": "Room not found."},
            status=404,
        )

    bookings = (
        Booking.objects.filter(room_id=room_id)
        .order_by("date_start")
        .values(
            "date_start",
            "date_end",
            booking_id=F("id"),
        )
    )

    return JsonResponse(list(bookings), safe=False)


@csrf_exempt
@require_json_methods(["DELETE"])
def delete_booking(request, booking_id):
    deleted_count, _ = Booking.objects.filter(id=booking_id).delete()

    if deleted_count == 0:
        return JsonResponse(
            {"error": "Booking not found."},
            status=404,
        )

    return JsonResponse({"deleted": True})

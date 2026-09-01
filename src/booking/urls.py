from django.urls import path

from booking import views

urlpatterns = [
    path('rooms/create', views.create_room, name='room-create'),
    path('rooms/list', views.list_rooms, name='room-list'),
    path('rooms/<int:room_id>', views.delete_room, name='room-delete'),
    path('bookings/create', views.create_booking, name='booking-create'),
    path('bookings/list', views.list_bookings, name='booking-list'),
    path('bookings/<int:booking_id>', views.delete_booking, name='booking-delete'),
]
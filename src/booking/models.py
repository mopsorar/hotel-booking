from django.db import models


class Room(models.Model):
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    date_start = models.DateField()
    date_end = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['room', 'date_start']),
        ]
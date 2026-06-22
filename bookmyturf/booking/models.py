from django.db import models

class Booking(models.Model):
    TURF_CHOICES = [
        ('5v5', '5 vs 5'),
        ('10v10', '10 vs 10'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    turf_type = models.CharField(max_length=10, choices=TURF_CHOICES)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
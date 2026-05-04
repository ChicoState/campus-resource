from django.db import models
from django.contrib.auth.models import User


class Resource(models.Model):
    CATEGORY_CHOICES = [
        ("Books", "Books"),
        ("Rooms", "Rooms"),
        ("Loanables", "Loanables"),
        ("Tutoring", "Tutoring"),
    ]

    AVAILABILITY_CHOICES = [
        ("Available", "Available"),
        ("Limited", "Limited"),
        ("Unavailable", "Unavailable"),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    desc = models.TextField()
    avail = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES)


class Reservation(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="reservations")
    user_email = models.EmailField()          # we store email; no auth system yet
    time_slot = models.CharField(max_length=20)   # e.g. "10:00 AM"
    date = models.DateField()                # which day the slot is for
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent double-booking the same resource/slot/date
        unique_together = ("resource", "time_slot", "date")

    def __str__(self):
        return f"{self.user_email} — {self.resource.name} @ {self.time_slot} on {self.date}"
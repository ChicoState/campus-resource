from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Resource(models.Model):
    def set_name(self, r_name):
        self.name = r_name
    def set_category(self, r_category):
        self.category = r_category
    def set_location(self, r_location):
        self.location = r_location
    def set_desc(self, r_desc):
        self.desc = r_desc
    def set_avail(self, r_avail):
        self.avail = r_avail
    def get_name(self):
        return self.name
    def get_category(self):
        return self.category
    def get_location(self):
        return self.location
    def get_desc(self):
        return self.desc
    def get_avail(self):
        return self.avail

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

    name = models.CharField(max_length = 200)
    category = models.CharField(max_length = 20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    desc = models.TextField()
    avail = models.CharField(max_length = 20, choices=AVAILABILITY_CHOICES)

class Reservation(models.Model):
    def set_resource(self, r_resource):
        self.resource = r_resource
    def set_timeSlot(self, r_timeSlot):
        self.timeSlot = r_timeSlot
    def set_timeReserved(self, r_timeReserved):
        self.timeReserved = r_timeReserved
    def get_resource(self):
        return self.resource
    def get_timeSlot(self):
        return self.timeSlot
    def get_timeReserved(self):
        return self.timeReserved
        
    TIME_SLOTS = [
        ("8:00 AM", "8:00 AM"),
        ("9:00 AM", "9:00 AM"),
        ("10:00 AM", "10:00 AM"),
        ("11:00 AM", "11:00 AM"),
        ("12:00 PM", "12:00 PM"),
        ("1:00 PM", "1:00 PM"),
        ("2:00 PM", "2:00 PM"),
        ("3:00 PM", "3:00 PM"),
        ("4:00 PM", "4:00 PM"),
        ("5:00 PM", "5:00 PM"),
        ("6:00 PM", "6:00 PM"),
        ("7:00 PM", "7:00 PM"),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    timeSlot = models.CharField(max_length = 20, choices = TIME_SLOTS)
    timeReserved = models.CharField(max_length = 200)
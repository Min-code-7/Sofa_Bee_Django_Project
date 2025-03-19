from django.db import models
from django.apps import apps
from users.models import UserProfile
from django.contrib.auth.models import User
class Address(models.Model):
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    detail_address = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.receiver_name} - {self.province} {self.city} {self.district}"

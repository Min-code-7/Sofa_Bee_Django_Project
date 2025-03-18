from django.db import models
from addresses.models import Address
from orders.models import Order
from users.models import UserProfile

#Create your models here.
class CaptchaModel(models.Model):
    email=models.EmailField()
    captcha=models.CharField(max_length=4)
    create_time=models.DateTimeField(auto_now_add=True)

# Create your models here.


from django.db import models
# Create your models here.
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('regular', 'normal user'),
        ('merchant', 'merchant user'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')    # type
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

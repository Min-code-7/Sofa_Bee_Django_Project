from django.db import models

# Create your models here.

class Consumer(models.Model):
    name=models.CharField(max_length=45)
    email=models.CharField(max_length=45)
    phone=models.CharField(max_length=45)
    create_time=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=45)
    password=models.CharField(max_length=45)
    images=models.FileField(upload_to='images/', null=True, blank=True)
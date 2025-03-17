from django.db import models

from addresses.models import Address
from users.models import Consumer

# Create your models here.
class Order(models.Model):
    order_time=models.DateTimeField(auto_now_add=True)
    order_status=models.BooleanField(default=False)
    total_price=models.FloatField(default=0)
    paid_time=models.DateTimeField(auto_now_add=True)
    created_time=models.DateTimeField(auto_now_add=True)
    consumer=models.ForeignKey(Consumer,on_delete=models.CASCADE,null=True)
    address=models.ForeignKey(Address,on_delete=models.CASCADE,null=True)


class Merchant(models.Model):
    shop_name=models.CharField(max_length=50)
    email=models.CharField(max_length=50,null=True)
    shop_description=models.CharField(max_length=50,null=True)


class Payment(models.Model):
    paid_price=models.FloatField(default=0)
    paid_time=models.DateTimeField(auto_now_add=True)
    paid_status=models.CharField(max_length=45)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)


class Product(models.Model):
    name=models.CharField(max_length=50)
    price=models.FloatField(default=0)
    image=models.CharField(max_length=45)
    description = models.CharField(max_length=45, null=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE,null=True)

class Order_Item(models.Model):
    price=models.FloatField(default=0)
    quantity=models.FloatField(default=0)
    unit_price=models.FloatField(default=0)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)



# orders/models.py
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('wechat', 'WeChat Pay'),
        ('alipay', 'Alipay'),
        ('cash', 'Cash on Delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)  # Record payment time
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='credit_card')
    shipping_address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)  # Order
    product_name = models.CharField(max_length=255)  # Product name
    quantity = models.PositiveIntegerField()  # Quantity
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Unit price
    # Removed product foreign key field because it doesn't exist in the database table

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

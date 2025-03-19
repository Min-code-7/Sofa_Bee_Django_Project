# orders/models.py
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

<<<<<<< HEAD
from products.models import Product

=======
>>>>>>> origin/feature-orders

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)  # 记录支付时间
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
<<<<<<< HEAD
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)  # 订单
    product_name = models.CharField(max_length=255)  # 商品名称
    quantity = models.PositiveIntegerField()  # 数量
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 单价
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
=======
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"
>>>>>>> origin/feature-orders

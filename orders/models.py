from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('canceled', '已取消'),
    ]

    PAYMENT_CHOICES = [
        ('credit_card', '信用卡'),
        ('paypal', 'PayPal'),
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联用户
    order_number = models.CharField(max_length=20, unique=True)  # 订单号
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # 总金额
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # 订单状态
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='credit_card')  # 支付方式
    created_at = models.DateTimeField(auto_now_add=True)  # 下单时间
    paid_at = models.DateTimeField(null=True, blank=True)  # 支付时间
    shipping_address = models.CharField(max_length=255, null=True, blank=True)  # 配送地址

    def __str__(self):
        return f'订单 {self.order_number} - 状态: {self.status}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)  # 订单
    product_name = models.CharField(max_length=255)  # 商品名称
    quantity = models.PositiveIntegerField()  # 数量
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 单价

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'



# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from products.models import Product  # 假设商品模型在 `products` app 里
'''
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
'''
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.get_price() for item in self.items.all())

    def get_total_items(self):
        return self.items.count()

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):

    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # quantity = models.PositiveIntegerField(default=1)
    # added_at = models.DateTimeField(auto_now_add=True)
    
    # def get_price(self):
        # return self.product.price * self.quantity

    # class Meta:
        # unique_together = ['cart', 'product']

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id_test = models.IntegerField(default=1)  # 存储产品ID
    product_name = models.CharField(max_length=255, null=True, blank=True)  # 存储产品名称
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 存储产品价格
    product_image = models.CharField(max_length=255, null=True, blank=True)  # 存储产品图片URL
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def get_price(self):
        return self.product_price * self.quantity if self.product_price else 0
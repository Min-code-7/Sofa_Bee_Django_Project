# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from products.models import Product, ProductVariant  # 
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
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # 恢复product字段，但设置为null=True, blank=True
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    # 恢复variant字段，但设置为null=True, blank=True
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product_id_test = models.IntegerField(default=0)  # 数据库中的字段
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    # 这些字段已经存在于数据库中
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_image = models.CharField(max_length=255, null=True, blank=True)

    def get_price(self):
        # First check if we have a stored price
        if self.product_price is not None:
            return self.product_price * self.quantity

        # Then check variant price
        if self.variant:
            return self.variant.price * self.quantity

        # Finally check product price
        if self.product:
            return self.product.price * self.quantity

        return 0

    class Meta:
        # 暂时移除约束，避免使用product_id字段
        pass

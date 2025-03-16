from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
#from products.models import Product  # 假设商品模型在 `products` app 里
'''
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
'''
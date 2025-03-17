from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# Create your models here.

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews") # related to the products
    user = models.ForeignKey(User, on_delete=models.CASCADE) # related user
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 5)]) # rate
    comment = models.TextField()    # comment
    created_at = models.DateTimeField(auto_now_add=True)    #time

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

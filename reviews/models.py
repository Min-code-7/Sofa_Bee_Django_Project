from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# Create your models here.
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")  # related to the products
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # related user
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # rate (1-5)
    comment = models.TextField()  # comment
    created_at = models.DateTimeField(auto_now_add=True)  # time
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)  # review by image

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

    def get_stars(self):
        return range(self.rating)

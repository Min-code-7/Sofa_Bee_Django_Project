from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def create_default_categories():
        default_categories = [
            {"name": "Makeup", "description": "Cosmetics, skincare products, and beauty accessories"},
            {"name": "Electronics", "description": "Gadgets, computers, phones and digital devices"},
            {"name": "Clothing", "description": "Apparel, fashion wear and accessories"},
            {"name": "Home & Kitchen", "description": "Household items, kitchen appliances, and home decor"},
            {"name": "Sports & Outdoors", "description": "Sports equipment, outdoor gear, and fitness accessories"},
            {"name": "Books", "description": "Fiction, non-fiction, textbooks, and other printed materials"},
            {"name": "Health & Personal Care", "description": "Vitamins, medications, personal hygiene products"},
            {"name": "Toys & Games", "description": "Children's toys, board games, and collectibles"},
            {"name": "Jewelry & Accessories", "description": "Watches, necklaces, earrings, and fashion accessories"},
            {"name": "Food & Beverages", "description": "Groceries, snacks, drinks, and specialty food items"},
            {"name": "Pet Supplies", "description": "Food, toys, and accessories for pets"},
            {"name": "Furniture", "description": "Chairs, tables, beds, and home furniture"},
            {"name": "Baby Products", "description": "Clothing, toys, and care products for babies and infants"},
            {"name": "Automotive", "description": "Car accessories, tools, and auto maintenance products"},
            {"name": "Office Supplies", "description": "Stationery, desk accessories, and office equipment"},
        ]

        for category in default_categories:
            Category.objects.get_or_create(name=category["name"], defaults={"description": category["description"]})

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
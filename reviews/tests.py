from django.test import TestCase
from products.models import Product, Category
from reviews.models import Review
from django.contrib.auth.models import User
from django.templatetags.static import static

# Create your tests here.
class ReviewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.makeup_category, _ = Category.objects.get_or_create(name="Makeup")
        cls.clothing_category, _ = Category.objects.get_or_create(name="Clothing")
        cls.electronics_category, _ = Category.objects.get_or_create(name="Electronics")

        cls.user = User.objects.create_user(username="testuser", password="password")


        cls.products = [
            Product.objects.create(
                name=f"Test Product {i+1}",
                description=f"This is product {i+1}",
                category=cls.makeup_category if i % 3 == 0 else
                          cls.clothing_category if i % 3 == 1 else
                          cls.electronics_category,
                price=99.99 + i * 10,
                image=static(f"products/images/pic{i+1}.png"),
            )
            for i in range(12)
        ]


        cls.reviews = [
            Review.objects.create(
                product=cls.products[i % len(cls.products)],
                user=cls.user,
                rating=(i % 5) + 1,
                comment=f"Test review {i+1}",
            )
            for i in range(5)
        ]

    def test_review_creation(self):
        self.assertEqual(Review.objects.count(), 5)
        self.assertEqual(self.reviews[0].product.category.name, "Makeup")


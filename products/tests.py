from django.test import TestCase
# from django.test import LiveServerTestCase
# from django.test import TransactionTestCase
from django.templatetags.static import static
from products.models import Product, Category
from django.db import connection

# from django.core.management import call_command

# Create your tests here.


class ProductTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.makeup_category = Category.objects.create(name="Makeup")
        cls.clothing_category = Category.objects.create(name="Clothing")
        cls.electronics_category = Category.objects.create(name="Electronics")

        cls.products = []
        for i in range(12):
            product = Product.objects.create(
                name=f"Test Product {i+1}",
                description=f"This is the {i+1} test product",
                category=cls.makeup_category if i % 3 == 0 else
                         cls.clothing_category if i % 3 == 1 else
                         cls.electronics_category,
                price=99.99 + i * 10,
                image=static(f"products/images/pic{i+1}.png"),
            )
            cls.products.append(product)

            connection.commit()

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 12)
        self.assertEqual(self.products[1].category.name, "Clothing")
        # self.assertEqual(self.products[1].category.name, "Clothing")



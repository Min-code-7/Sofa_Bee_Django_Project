from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem
from products.models import Product, Category

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        self.order = Order.objects.create(
            user=self.user,
            order_number="ORD12345",
            total_price=Decimal("299.97"),
            status="pending",
            payment_method="credit_card",
            shipping_address="123 Test Street, Test City, Test Province",
        )
    
    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.order_number, "ORD12345")
        self.assertEqual(self.order.total_price, Decimal("299.97"))
        self.assertEqual(self.order.status, "pending")
        self.assertEqual(self.order.payment_method, "credit_card")
        self.assertEqual(self.order.shipping_address, "123 Test Street, Test City, Test Province")
        self.assertIsNone(self.order.paid_at)
        self.assertIsNotNone(self.order.created_at)
        self.assertEqual(str(self.order), f"Order ORD12345 - testuser")
    
    def test_order_status_choices(self):
        # Test all possible status values
        status_choices = ["pending", "paid", "shipped", "completed"]
        
        for status in status_choices:
            self.order.status = status
            self.order.save()
            self.assertEqual(self.order.status, status)
    
    def test_payment_method_choices(self):
        # Test all possible payment method values
        payment_choices = ["credit_card", "paypal", "wechat", "alipay", "cash"]
        
        for payment in payment_choices:
            self.order.payment_method = payment
            self.order.save()
            self.assertEqual(self.order.payment_method, payment)
    
    def test_order_payment(self):
        # Test marking an order as paid
        self.assertIsNone(self.order.paid_at)
        
        # Update the order to paid status and set paid_at time
        self.order.status = "paid"
        self.order.paid_at = timezone.now()
        self.order.save()
        
        self.assertEqual(self.order.status, "paid")
        self.assertIsNotNone(self.order.paid_at)

class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal("99.99"),
            category=self.category,
            seller=self.user,
            stock=10
        )
        
        self.order = Order.objects.create(
            user=self.user,
            order_number="ORD12345",
            total_price=Decimal("299.97"),
            status="pending",
            payment_method="credit_card",
            shipping_address="123 Test Street, Test City, Test Province",
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_name="Test Product",
            quantity=3,
            price=Decimal("99.99")
        )
    
    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product_name, "Test Product")
        self.assertEqual(self.order_item.quantity, 3)
        self.assertEqual(self.order_item.price, Decimal("99.99"))
        self.assertEqual(str(self.order_item), "Test Product x 3")
    
    def test_multiple_order_items(self):
        # Add another item to the order
        order_item2 = OrderItem.objects.create(
            order=self.order,
            product_name="Another Product",
            quantity=1,
            price=Decimal("149.99")
        )
        
        # Check that both items are associated with the order
        order_items = self.order.items.all()
        self.assertEqual(order_items.count(), 2)
        self.assertIn(self.order_item, order_items)
        self.assertIn(order_item2, order_items)
        
        # Calculate the total price of all items
        total_price = sum(item.price * item.quantity for item in order_items)
        expected_total = Decimal("99.99") * 3 + Decimal("149.99") * 1
        self.assertEqual(total_price, expected_total)

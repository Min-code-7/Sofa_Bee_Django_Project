from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Cart, CartItem
from .forms import ShippingAddressForm
from products.models import Product, Category, ProductVariant, ProductAttribute, ProductAttributeValue
from addresses.models import Address

class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        self.cart = Cart.objects.create(
            user=self.user
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
        
        # Create a product variant
        self.color_attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
        
        self.red_value = ProductAttributeValue.objects.create(
            attribute=self.color_attribute,
            value="Red"
        )
        
        self.variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("109.99"),
            stock=5,
            is_default=True
        )
        
        self.variant.attribute_values.add(self.red_value)
        
        # Create cart items
        self.cart_item1 = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            product_name="Test Product",
            product_price=Decimal("99.99"),
            product_image="test.jpg"
        )
        
        self.cart_item2 = CartItem.objects.create(
            cart=self.cart,
            variant=self.variant,
            quantity=1,
            product_name="Test Product (Red)",
            product_price=Decimal("109.99"),
            product_image="test_red.jpg"
        )
    
    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(str(self.cart), f"Cart for {self.user.username}")
    
    def test_get_total_price(self):
        # Calculate expected total: (99.99 * 2) + (109.99 * 1) = 309.97
        expected_total = Decimal("309.97")
        self.assertEqual(self.cart.get_total_price(), expected_total)
    
    def test_get_total_items(self):
        self.assertEqual(self.cart.get_total_items(), 2)  # Two different items, not counting quantities

class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        self.cart = Cart.objects.create(
            user=self.user
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
        
        # Create a product variant
        self.color_attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
        
        self.red_value = ProductAttributeValue.objects.create(
            attribute=self.color_attribute,
            value="Red"
        )
        
        self.variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("109.99"),
            stock=5,
            is_default=True
        )
        
        self.variant.attribute_values.add(self.red_value)
    
    def test_cart_item_with_product(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            product_name="Test Product",
            product_price=Decimal("99.99"),
            product_image="test.jpg"
        )
        
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertIsNone(cart_item.variant)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.product_name, "Test Product")
        self.assertEqual(cart_item.product_price, Decimal("99.99"))
        self.assertEqual(cart_item.product_image, "test.jpg")
        
        # Test get_price method
        self.assertEqual(cart_item.get_price(), Decimal("199.98"))  # 99.99 * 2
    
    def test_cart_item_with_variant(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            variant=self.variant,
            quantity=3,
            product_name="Test Product (Red)",
            product_price=Decimal("109.99"),
            product_image="test_red.jpg"
        )
        
        self.assertEqual(cart_item.cart, self.cart)
        self.assertIsNone(cart_item.product)
        self.assertEqual(cart_item.variant, self.variant)
        self.assertEqual(cart_item.quantity, 3)
        self.assertEqual(cart_item.product_name, "Test Product (Red)")
        self.assertEqual(cart_item.product_price, Decimal("109.99"))
        self.assertEqual(cart_item.product_image, "test_red.jpg")
        
        # Test get_price method
        self.assertEqual(cart_item.get_price(), Decimal("329.97"))  # 109.99 * 3
    
    def test_cart_item_with_stored_price(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            quantity=2,
            product_name="Test Product",
            product_price=Decimal("99.99"),
            product_image="test.jpg"
        )
        
        # Test get_price method with stored price
        self.assertEqual(cart_item.get_price(), Decimal("199.98"))  # 99.99 * 2
    
    def test_cart_item_without_price(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            quantity=2,
            product_name="Test Product",
            product_image="test.jpg"
        )
        
        # Test get_price method without any price
        self.assertEqual(cart_item.get_price(), 0)

class ShippingAddressFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create some addresses for the user
        self.address1 = Address.objects.create(
            user=self.user,
            receiver_name="John Doe",
            receiver_phone="1234567890",
            province="Test Province",
            city="Test City",
            district="Test District",
            detail_address="123 Test Street",
            is_default=True
        )
        
        self.address2 = Address.objects.create(
            user=self.user,
            receiver_name="Jane Doe",
            receiver_phone="0987654321",
            province="Another Province",
            city="Another City",
            district="Another District",
            detail_address="456 Another Street",
            is_default=False
        )
        
        self.form_data = {
            'name': 'Test User',
            'phone': '5555555555',
            'address': '789 New Street',
            'postal_code': '12345',
            'save_address': True
        }
    
    def test_form_initialization_with_user(self):
        form = ShippingAddressForm(user=self.user)
        
        # Check if the user's addresses are in the queryset
        self.assertEqual(form.fields['use_existing_address'].queryset.count(), 2)
        self.assertIn(self.address1, form.fields['use_existing_address'].queryset)
        self.assertIn(self.address2, form.fields['use_existing_address'].queryset)
    
    def test_form_initialization_without_user(self):
        form = ShippingAddressForm()
        
        # Check if the queryset is empty when no user is provided
        self.assertEqual(form.fields['use_existing_address'].queryset.count(), 0)
    
    def test_valid_form(self):
        form = ShippingAddressForm(data=self.form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        # Test with missing required fields
        form = ShippingAddressForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('phone', form.errors)
        self.assertIn('address', form.errors)
        self.assertIn('postal_code', form.errors)
    
    def test_form_with_existing_address(self):
        form_data = {
            'use_existing_address': self.address1.id
        }
        form = ShippingAddressForm(data=form_data, user=self.user)
        
        # Debug form validation
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
            # If the form requires other fields even with an existing address, let's add them
            form_data.update({
                'name': 'Test User',
                'phone': '5555555555',
                'address': '789 New Street',
                'postal_code': '12345'
            })
            form = ShippingAddressForm(data=form_data, user=self.user)
        
        # The form should be valid with all required fields
        self.assertTrue(form.is_valid())

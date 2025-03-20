from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import Category, Product, ProductAttribute, ProductAttributeValue, ProductVariant
from .forms import ProductForm, ProductAttributeForm, ProductAttributeValueForm, ProductVariantForm, ProductWithVariantForm

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.description, "Test Description")
        self.assertEqual(str(self.category), "Test Category")
    
    def test_create_default_categories(self):
        # Clear existing categories
        Category.objects.all().delete()
        
        # Create default categories
        Category.create_default_categories()
        
        # Check if default categories were created
        self.assertTrue(Category.objects.filter(name="Electronics").exists())
        self.assertTrue(Category.objects.filter(name="Clothing").exists())
        self.assertEqual(Category.objects.count(), 15)  # There should be 15 default categories

class ProductModelTest(TestCase):
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
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "Test Description")
        self.assertEqual(self.product.price, Decimal("99.99"))
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.seller, self.user)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(str(self.product), "Test Product")
    
    def test_reduce_stock(self):
        # Test successful stock reduction
        result = self.product.reduce_stock(5)
        self.assertTrue(result)
        self.assertEqual(self.product.stock, 5)
        
        # Test stock reduction with insufficient stock
        result = self.product.reduce_stock(10)
        self.assertFalse(result)
        self.assertEqual(self.product.stock, 5)  # Stock should remain unchanged

class ProductAttributeModelTest(TestCase):
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
        
        self.attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
    
    def test_attribute_creation(self):
        self.assertEqual(self.attribute.product, self.product)
        self.assertEqual(self.attribute.name, "Color")
        self.assertEqual(str(self.attribute), "Test Product - Color")

class ProductAttributeValueModelTest(TestCase):
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
        
        self.attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
        
        self.attribute_value = ProductAttributeValue.objects.create(
            attribute=self.attribute,
            value="Red"
        )
    
    def test_attribute_value_creation(self):
        self.assertEqual(self.attribute_value.attribute, self.attribute)
        self.assertEqual(self.attribute_value.value, "Red")
        self.assertEqual(str(self.attribute_value), "Color: Red")

class ProductVariantModelTest(TestCase):
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
        
        self.color_attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
        
        self.size_attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Size"
        )
        
        self.red_value = ProductAttributeValue.objects.create(
            attribute=self.color_attribute,
            value="Red"
        )
        
        self.large_value = ProductAttributeValue.objects.create(
            attribute=self.size_attribute,
            value="Large"
        )
        
        self.variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("109.99"),
            stock=5,
            is_default=True
        )
        
        self.variant.attribute_values.add(self.red_value, self.large_value)
    
    def test_variant_creation(self):
        self.assertEqual(self.variant.product, self.product)
        self.assertEqual(self.variant.price, Decimal("109.99"))
        self.assertEqual(self.variant.stock, 5)
        self.assertTrue(self.variant.is_default)
        self.assertEqual(self.variant.attribute_values.count(), 2)
        self.assertIn(self.red_value, self.variant.attribute_values.all())
        self.assertIn(self.large_value, self.variant.attribute_values.all())
        self.assertEqual(str(self.variant), "Test Product - Color: Red, Size: Large")
    
    def test_default_variant_uniqueness(self):
        # Create another variant with is_default=True
        new_variant = ProductVariant.objects.create(
            product=self.product,
            price=Decimal("119.99"),
            stock=3,
            is_default=True
        )
        
        # Refresh the original variant from the database
        self.variant.refresh_from_db()
        
        # The original variant should no longer be default
        self.assertFalse(self.variant.is_default)
        self.assertTrue(new_variant.is_default)
    
    def test_reduce_stock(self):
        # Test successful stock reduction
        result = self.variant.reduce_stock(3)
        self.assertTrue(result)
        self.assertEqual(self.variant.stock, 2)
        
        # Test stock reduction with insufficient stock
        result = self.variant.reduce_stock(5)
        self.assertFalse(result)
        self.assertEqual(self.variant.stock, 2)  # Stock should remain unchanged

class ProductFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )
        
        self.form_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'category': self.category.id,
            'price': '99.99',
            'stock': '10',
        }
        
        # Create a non-empty file for testing
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',  # Non-empty content
            content_type='image/jpeg'
        )
    
    def test_valid_form(self):
        # Test form validation without image
        form_data = self.form_data.copy()
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        # Test with missing required fields
        form = ProductForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('price', form.errors)

class ProductAttributeFormTest(TestCase):
    def test_valid_form(self):
        form = ProductAttributeForm(data={'name': 'Color'})
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        form = ProductAttributeForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

class ProductAttributeValueFormTest(TestCase):
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
        
        self.attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
    
    def test_valid_form(self):
        form = ProductAttributeValueForm(data={
            'attribute': self.attribute.id,
            'value': 'Red'
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        form = ProductAttributeValueForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('attribute', form.errors)
        self.assertIn('value', form.errors)

class ProductVariantFormTest(TestCase):
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
        
        self.color_attribute = ProductAttribute.objects.create(
            product=self.product,
            name="Color"
        )
        
        self.red_value = ProductAttributeValue.objects.create(
            attribute=self.color_attribute,
            value="Red"
        )
    
    def test_valid_form(self):
        form = ProductVariantForm(data={
            'price': '109.99',
            'stock': '5',
            'is_default': True,
            'attribute_values': [self.red_value.id]
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        form = ProductVariantForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertIn('stock', form.errors)
        self.assertIn('attribute_values', form.errors)

class ProductWithVariantFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )
        
        self.form_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'category': self.category.id,
            'has_variants': True
        }
        
        # Create a non-empty file for testing
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',  # Non-empty content
            content_type='image/jpeg'
        )
    
    def test_valid_form(self):
        # Test form validation without image
        form_data = self.form_data.copy()
        form = ProductWithVariantForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        # Test with missing required fields
        form = ProductWithVariantForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('category', form.errors)

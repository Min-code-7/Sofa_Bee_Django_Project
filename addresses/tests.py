from django.test import TestCase
from django.contrib.auth.models import User
from .models import Address

class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
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
    
    def test_address_creation(self):
        self.assertEqual(self.address1.user, self.user)
        self.assertEqual(self.address1.receiver_name, "John Doe")
        self.assertEqual(self.address1.receiver_phone, "1234567890")
        self.assertEqual(self.address1.province, "Test Province")
        self.assertEqual(self.address1.city, "Test City")
        self.assertEqual(self.address1.district, "Test District")
        self.assertEqual(self.address1.detail_address, "123 Test Street")
        self.assertTrue(self.address1.is_default)
        
        self.assertEqual(self.address2.user, self.user)
        self.assertEqual(self.address2.receiver_name, "Jane Doe")
        self.assertEqual(self.address2.receiver_phone, "0987654321")
        self.assertEqual(self.address2.province, "Another Province")
        self.assertEqual(self.address2.city, "Another City")
        self.assertEqual(self.address2.district, "Another District")
        self.assertEqual(self.address2.detail_address, "456 Another Street")
        self.assertFalse(self.address2.is_default)
    
    def test_address_string_representation(self):
        expected_str = "John Doe - Test Province Test City Test District"
        self.assertEqual(str(self.address1), expected_str)
        
        expected_str2 = "Jane Doe - Another Province Another City Another District"
        self.assertEqual(str(self.address2), expected_str2)
    
    def test_multiple_default_addresses(self):
        # Create a new default address for the same user
        address3 = Address.objects.create(
            user=self.user,
            receiver_name="New User",
            receiver_phone="5555555555",
            province="New Province",
            city="New City",
            district="New District",
            detail_address="789 New Street",
            is_default=True
        )
        
        # Refresh the first address from the database
        self.address1.refresh_from_db()
        
        # The first address should still be default (Django doesn't automatically enforce uniqueness)
        # In a real application, you would need to handle this in the view or with a signal
        self.assertTrue(self.address1.is_default)
        self.assertTrue(address3.is_default)
        
        # Count the number of default addresses for this user
        default_count = Address.objects.filter(user=self.user, is_default=True).count()
        self.assertEqual(default_count, 2)
    
    def test_address_without_user(self):
        # Create an address without a user (for guest checkout)
        address = Address.objects.create(
            receiver_name="Guest User",
            receiver_phone="1112223333",
            province="Guest Province",
            city="Guest City",
            district="Guest District",
            detail_address="999 Guest Street",
            is_default=False
        )
        
        self.assertIsNone(address.user)
        self.assertEqual(address.receiver_name, "Guest User")
        self.assertEqual(address.receiver_phone, "1112223333")
        self.assertEqual(address.province, "Guest Province")
        self.assertEqual(address.city, "Guest City")
        self.assertEqual(address.district, "Guest District")
        self.assertEqual(address.detail_address, "999 Guest Street")
        self.assertFalse(address.is_default)

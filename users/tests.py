from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile
from .forms import UserRegisterForm

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            user_type="regular",
            phone_number="1234567890",
            avatar="test_avatar.png"
        )
    
    def test_user_profile_creation(self):
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.user_type, "regular")
        self.assertEqual(self.user_profile.phone_number, "1234567890")
        self.assertEqual(self.user_profile.avatar, "test_avatar.png")
        self.assertEqual(str(self.user_profile), "testuser - normal user")
    
    def test_user_profile_types(self):
        # Test regular user profile
        self.assertEqual(self.user_profile.get_user_type_display(), "normal user")
        
        # Test merchant user profile
        merchant_user = User.objects.create_user(
            username="merchant",
            email="merchant@example.com",
            password="merchantpass"
        )
        
        merchant_profile = UserProfile.objects.create(
            user=merchant_user,
            user_type="merchant",
            phone_number="9876543210"
        )
        
        self.assertEqual(merchant_profile.get_user_type_display(), "merchant user")
        self.assertEqual(str(merchant_profile), "merchant - merchant user")
    
    def test_default_avatar(self):
        # Create a user profile without specifying an avatar
        new_user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="newpassword"
        )
        
        new_profile = UserProfile.objects.create(
            user=new_user,
            user_type="regular",
            phone_number="5555555555"
        )
        
        # Check if the default avatar is set
        self.assertEqual(new_profile.avatar, "default.png")

class UserRegisterFormTest(TestCase):
    def setUp(self):
        self.form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'verification_code': '123456',
            'phone_number': '1234567890',
            'user_type': 'regular'
        }
    
    def test_valid_form(self):
        form = UserRegisterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        # Test with mismatched passwords
        form_data = self.form_data.copy()
        form_data['confirm_password'] = 'differentpassword'
        
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('The passwords entered do not match!', form.non_field_errors())
    
    def test_missing_required_fields(self):
        # Test with missing required fields
        form = UserRegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)
        self.assertIn('confirm_password', form.errors)
        self.assertIn('verification_code', form.errors)
        self.assertIn('phone_number', form.errors)
    
    def test_email_validation(self):
        # Test with invalid email format
        form_data = self.form_data.copy()
        form_data['email'] = 'invalid-email'
        
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_user_type_choices(self):
        # Test with valid user types
        for user_type in ['regular', 'merchant']:
            form_data = self.form_data.copy()
            form_data['user_type'] = user_type
            
            form = UserRegisterForm(data=form_data)
            self.assertTrue(form.is_valid())
        
        # Test with invalid user type
        form_data = self.form_data.copy()
        form_data['user_type'] = 'invalid_type'
        
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('user_type', form.errors)

import os
import django
import unittest

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sofa_Bee_Django_Project.settings')
django.setup()

# Import test modules
from products.tests import (
    CategoryModelTest, ProductModelTest, ProductAttributeModelTest,
    ProductAttributeValueModelTest, ProductVariantModelTest,
    ProductFormTest, ProductAttributeFormTest, ProductAttributeValueFormTest,
    ProductVariantFormTest, ProductWithVariantFormTest
)

from cart.tests import (
    CartModelTest, CartItemModelTest, ShippingAddressFormTest
)

from users.tests import (
    UserProfileModelTest, UserRegisterFormTest
)

from addresses.tests import (
    AddressModelTest
)

from orders.tests import (
    OrderModelTest, OrderItemModelTest
)

from reviews.tests import (
    ReviewModelTest, ReviewFormTest
)

# Create test suite
def create_test_suite():
    test_suite = unittest.TestSuite()
    
    # Add product tests
    test_suite.addTest(unittest.makeSuite(CategoryModelTest))
    test_suite.addTest(unittest.makeSuite(ProductModelTest))
    test_suite.addTest(unittest.makeSuite(ProductAttributeModelTest))
    test_suite.addTest(unittest.makeSuite(ProductAttributeValueModelTest))
    test_suite.addTest(unittest.makeSuite(ProductVariantModelTest))
    test_suite.addTest(unittest.makeSuite(ProductFormTest))
    test_suite.addTest(unittest.makeSuite(ProductAttributeFormTest))
    test_suite.addTest(unittest.makeSuite(ProductAttributeValueFormTest))
    test_suite.addTest(unittest.makeSuite(ProductVariantFormTest))
    test_suite.addTest(unittest.makeSuite(ProductWithVariantFormTest))
    
    # Add cart tests
    test_suite.addTest(unittest.makeSuite(CartModelTest))
    test_suite.addTest(unittest.makeSuite(CartItemModelTest))
    test_suite.addTest(unittest.makeSuite(ShippingAddressFormTest))
    
    # Add user tests
    test_suite.addTest(unittest.makeSuite(UserProfileModelTest))
    test_suite.addTest(unittest.makeSuite(UserRegisterFormTest))
    
    # Add address tests
    test_suite.addTest(unittest.makeSuite(AddressModelTest))
    
    # Add order tests
    test_suite.addTest(unittest.makeSuite(OrderModelTest))
    test_suite.addTest(unittest.makeSuite(OrderItemModelTest))
    
    # Add review tests
    test_suite.addTest(unittest.makeSuite(ReviewModelTest))
    test_suite.addTest(unittest.makeSuite(ReviewFormTest))
    
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = create_test_suite()
    runner.run(test_suite)

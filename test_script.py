import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sofa_Bee_Django_Project.settings')
django.setup()

# Import test module
from products.tests import CategoryModelTest

# Run test
if __name__ == '__main__':
    import unittest
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

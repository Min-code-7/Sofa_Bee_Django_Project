# cart/forms.py
from django import forms

class ShippingAddressForm(forms.Form):
    name = forms.CharField(max_length=100, label="Full name")
    phone = forms.CharField(max_length=20, label="Phone number")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Delivery address")
    postal_code = forms.CharField(max_length=10, label="Postcode")

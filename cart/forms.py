# cart/forms.py
from django import forms
from addresses.models import Address

class ShippingAddressForm(forms.Form):
    name = forms.CharField(max_length=100, label="Full Name")
    phone = forms.CharField(max_length=20, label="Phone Number")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Address")
    postal_code = forms.CharField(max_length=10, label="Postal Code")
    save_address = forms.BooleanField(required=False, label="Save this address to my profile")
    
    # Field for selecting existing address
    use_existing_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),  # Will be set in __init__
        required=False,
        empty_label="-- Select a saved address --",
        label="Use a saved address"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        
        # If user is provided, set the queryset for existing addresses
        if user and user.is_authenticated:
            self.fields['use_existing_address'].queryset = Address.objects.filter(user=user)

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="email")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="confirm password")
    verification_code = forms.CharField(label="verification code", required=True)
    phone_number = forms.CharField(max_length=15, label="Phone number", required=True)
    user_type = forms.ChoiceField(
        choices=[('regular', 'normal user'), ('merchant', 'merchant user')],
        initial='regular',
        widget=forms.HiddenInput()
    )
   
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password', 'verification_code', 'user_type']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("The passwords entered twice are inconsistent!")

        return cleaned_data
    
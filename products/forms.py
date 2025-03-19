from django import forms
from .models import Product, Category, ProductAttribute, ProductAttributeValue, ProductVariant

class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=True, empty_label=None, label="Select a category"
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductAttributeValueForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeValue
        fields = ['attribute', 'value']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductVariantForm(forms.ModelForm):

    attribute_values = forms.ModelMultipleChoiceField(
        queryset=ProductAttributeValue.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Attribute Values Group"
    )

    class Meta:
        model = ProductVariant
        fields = ['price', 'stock', 'is_default', 'attribute_values']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'price': 'Price',
            'stock': 'Stock',
            'is_default': 'Set Default',
        }


class ProductWithVariantForm(forms.Form):

    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


    has_variants = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Use Variants"
    )
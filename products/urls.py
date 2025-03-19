from django.urls import path, include
from .views import (
    product_list, product_detail, product_search, add_product,
    filter_category, edit_product, manage_variants, delete_variant,
    manage_products, delete_attribute, delete_attribute_value
)

app_name = "products"
urlpatterns = [
    path('', product_list, name='product_list'),
    path('<int:product_id>/', product_detail, name='product_detail'),
    path('search/',product_search, name='product_search'),
    path('add/', add_product, name='add_product'),
    path('filter/', filter_category, name='filter_category'),
    path('manage/', manage_products, name='manage_products'),
    path('edit/<int:product_id>/', edit_product, name='edit_product'),
    path('variants/<int:product_id>/', manage_variants, name='manage_variants'),
    path('variant/<int:variant_id>/delete/', delete_variant, name='delete_variant'),
    path('attribute/<int:attribute_id>/delete/', delete_attribute, name='delete_attribute'),
    path('attribute_value/<int:value_id>/delete/', delete_attribute_value, name='delete_attribute_value'),
    path('reviews/', include('reviews.urls')),
]
from django.urls import path, include
from .views import product_list, product_detail, product_search, add_product, filter_category

urlpatterns = [
    path('', product_list, name='product_list'),
    path('<int:product_id>/', product_detail, name='product_detail'),
    path('search/',product_search, name='product_search'),
    path('add/', add_product, name='add_product'),
    path('filter/', filter_category, name='filter_category'),
    path('reviews/', include('reviews.urls')),
]
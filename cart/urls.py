# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('search/', views.cart_search, name='cart_search'),
    path('checkout/', views.checkout, name='checkout'),
    path('shipping/', views.shipping, name='shipping'),
    path('payment/', views.payment, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
]

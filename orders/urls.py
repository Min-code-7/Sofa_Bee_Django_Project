# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/confirm/', views.confirm_receipt, name='confirm_receipt'),
]

from django.urls import path
from .views import create_order, list_orders, order_detail, update_order, delete_order, pay_order

urlpatterns = [
    path('create/', create_order, name='create_order'),
    path('list/', list_orders, name='list_orders'),
    path('<str:order_number>/', order_detail, name='order_detail'),
    path('<str:order_number>/update/', update_order, name='update_order'),
    path('<str:order_number>/delete/', delete_order, name='delete_order'),
    path('<str:order_number>/pay/', pay_order, name='pay_order'),
]

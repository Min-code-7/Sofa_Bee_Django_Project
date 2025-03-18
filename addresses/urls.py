
from django.urls import path, re_path

from .views import modify_address,add_address,delete_address

urlpatterns = [

    path('modify_address/<int:address_id>/', modify_address, name='modify_address'),
    path('add_address/<int:id>/', add_address, name='add_address'),
    path('delete_address/<int:address_id>/', delete_address, name='delete_address'),
]

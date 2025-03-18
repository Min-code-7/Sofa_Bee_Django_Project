from django.urls import path
from .views import profiles, modify, send_email_captcha, compare_code, history_order, order_detail

urlpatterns = [
    path('<int:id>/', profiles, name='profiles'),
    path('modify/<int:id>/', modify, name='modify_profile'),
    path('modify/<int:id>/captcha/', send_email_captcha, name='email_captcha'),

    path('history_order/<int:id>/', history_order, name='history_order'),
    path('order_detail/<int:id>/', order_detail, name='history_order_detail'),

]
from django.urls import path
from .views import profiles, modify, send_email_captcha, compare_code, history_order, order_detail

urlpatterns = [
    path('<int:id>/', profiles, name='profiles'),
    path('modify/', modify, name='modify_profile'),
    path('modify/captcha/', send_email_captcha, name='email_captcha'),
    path('verify_captcha/', compare_code, name='verify_captcha'),
    path('history_order/', history_order, name='history_order'),
    path('order_detail/<int:id>/', order_detail, name='history_order_detail'),
]

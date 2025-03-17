from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),      # login
    path('logout/', views.user_logout, name='logout'),  # logout
    path("send_verification_code/", views.send_verification_code, name="send_verification_code"),
]
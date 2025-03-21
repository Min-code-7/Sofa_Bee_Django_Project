from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),      # login
    path('logout/', views.user_logout, name='logout'),  # logout
    path("send_verification_code/", views.send_verification_code, name="send_verification_code"),
    path("check_username/", views.check_username, name="check_username"),
]

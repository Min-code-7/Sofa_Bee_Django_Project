"""
URL configuration for Sofa_Bee_Django_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from profiles import views as profiles_views
from profiles.views import profiles
from addresses import views as addresses_views
from orders import views as orders_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles/<int:id>', profiles_views.profiles,name='profiles'),
    path('profile/modify/<int:id>/', profiles_views.modify, name='modify_profile'),
    path('profile/modify/<int:id>/captcha/', profiles_views.send_email_captcha, name='email_captcha'),
    path('verify_captcha/',profiles_views.compare_code, name='verify_code'),
    path('modify_address/<int:address_id>/',addresses_views.modify_address, name='modify_address'),
    path('profiles/add_address/<int:id>/',addresses_views.add_address,name='add_address'),
    path('delete_address/<int:address_id>/',addresses_views.delete_address,name='delete_address'),
    path('history_order/<int:id>/',orders_views.history_order,name='history_order'),
    path('order_detail/<int:id>/',orders_views.order_detail,name='order_detail'),


]

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_price', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('order_number', 'user__username','status')


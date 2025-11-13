from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'customer', 'receiver_name', 'status', 'payment_status', 'amount', 'created_at', 'updated_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('barcode', 'receiver_name', 'customer__username')
    ordering = ('-created_at',)
    readonly_fields = ('barcode', 'created_at', 'updated_at')


admin.site.register(Order, OrderAdmin)

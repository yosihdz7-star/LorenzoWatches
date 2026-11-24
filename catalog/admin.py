from django.contrib import admin
from .models import ContactMessage, Order, OrderItem, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'price', 'category', 'stock')
    search_fields = ('name', 'brand', 'category')
    list_filter = ('brand', 'category')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
    ordering = ('-created_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'unit_price', 'quantity', 'subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'email', 'total', 'payment_method', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'customer_name', 'email')
    readonly_fields = ('order_number', 'total', 'payment_status', 'created_at')
    inlines = [OrderItemInline]

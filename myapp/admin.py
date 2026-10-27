from django.contrib import admin
from .models import Table, MenuItem, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'status', 'priority', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Table)
admin.site.register(MenuItem)

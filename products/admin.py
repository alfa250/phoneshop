from django.contrib import admin
from .models import Product, Category, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'sale_price',
        'is_sale',
        'stock',
    )

    list_filter = (
        'category',
    )

    search_fields = (
        'name',
        'description',
    )

    list_editable = (
        'stock',
        'is_sale'
    )

    def current_price(self, obj):
        return obj.current_price

    current_price.short_description = 'Current Price'


admin.site.register(Category)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'subtotal_display',
    )
    def subtotal_display(self, obj):
        if obj.quantity is None or obj.price is None:
            return '-'

        return obj.quantity * obj.price

    subtotal_display.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'user',
        'date_created',
        'status',
        'total',
    )

    list_filter = (
        'status',
        'date_created',
    )


    search_fields = (
        'order_number',
        'full_name',
        'phone',
        'user__username',
    )

    ordering = (
        '-date_created',
    )

    inlines = (
        OrderItemInline,
    )


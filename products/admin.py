from django.contrib import admin
from .models import Product, Category, Order, OrderItem


class StockStatusFilter(admin.SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock__gt=5)

        if self.value() == 'low_stock':
            return queryset.filter(stock__gt=0, stock__lte=5)

        if self.value() == 'out_of_stock':
            return queryset.filter(stock=0)

        return queryset

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'sale_price',
        'is_sale',
        'stock',
        'stock_status',
    )

    list_filter = (
        'category',
        'is_sale',
        StockStatusFilter
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

    # def is_low_stock(self, obj):
    #     return obj.stock <= 5
    # is_low_stock.short_description = 'Low Stock'

    def stock_status(self, obj):
        if obj.stock == 0:
            return 'Out of Stock'
        elif obj.stock <= 5:
            return 'Low Stock'
        return 'In Stock'

    stock_status.short_description = 'Stock Status'




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


    def save_model(self, request, obj, form, change):
        if change:
            old_order = Order.objects.get(pk=obj.pk)

            # A canceled order cannot be reactivated.
            if old_order.status == Order.StatusChoices.CANCELED:
                obj.status = Order.StatusChoices.CANCELED

            # Restore stock when an order is canceled.
            if (
                old_order.status != Order.StatusChoices.CANCELED
                and obj.status == Order.StatusChoices.CANCELED
            ):
                for item in obj.items.select_related('product'):
                    item.product.stock += item.quantity
                    item.product.save()

        super().save_model(request, obj, form, change)

    def mark_as_confirmed(self, request, queryset):
        queryset.filter(
            status=Order.StatusChoices.PENDING
        ).update(
            status=Order.StatusChoices.CONFIRMED)
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_as_canceled(self, request, queryset):
        for order in queryset:
            if order.status == Order.StatusChoices.CANCELED:
                continue

            for item in order.items.select_related('product'):
                item.product.stock += item.quantity
                item.product.save()

            order.status = Order.StatusChoices.CANCELED
            order.save(update_fields=['status'])
    
    mark_as_canceled.short_description = (
    "Cancel selected orders and restore stock")
        
    actions = ['mark_as_confirmed',
                'mark_as_canceled']

    nlines = (OrderItemInline,)

    ordering = ('-date_created',)

    admin.site.register(Category)


    
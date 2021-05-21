from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['payment', 'user',
                       'product', 'quantity', 'product_price']
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'first_name', 'last_name', 'phone_number', 'email', 'adress_line', 'city',
                    'state', 'country', 'postal_code', 'order_total', 'tax', 'is_orderd', 'created_at')

    list_filter = ['status', 'is_orderd']

    search_fields = ['order_number', 'first_name',
                     'last_name', 'phone_number', 'email']

    list_per_page = 20

    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)

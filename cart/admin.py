from django.contrib import admin
from . import models


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'on_created')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantite', 'is_active')


admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.CartItem, CartItemAdmin)

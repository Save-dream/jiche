from django.contrib import admin

from apps.shops.models import Shop, ShopApplication


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_name', 'phone', 'shop_status', 'approved_at')
    list_filter = ('shop_status', 'shop_type')
    search_fields = ('name', 'contact_name', 'phone')


@admin.register(ShopApplication)
class ShopApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_name', 'phone', 'application_status', 'applied_at')
    list_filter = ('application_status', 'shop_type')
    search_fields = ('contact_name', 'phone', 'user__nickname')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import AuthLoginTicket, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'id',
        'nickname',
        'phone',
        'is_staff',
        'is_super_staff',
        'shop_status',
        'last_login_platform',
        'created_at',
    )
    list_filter = ('is_staff', 'is_super_staff', 'shop_status', 'is_deleted')
    search_fields = ('nickname', 'phone', 'unionid', 'mp_openid', 'web_openid', 'internal_username')
    ordering = ('-id',)
    fieldsets = (
        (None, {'fields': ('internal_username', 'password')}),
        ('微信信息', {'fields': ('unionid', 'mp_openid', 'web_openid', 'nickname', 'avatar', 'phone')}),
        ('权限', {'fields': ('is_staff', 'is_super_staff', 'staff_granted_by', 'staff_granted_at')}),
        ('商家状态', {'fields': ('shop_status', 'shop_id')}),
        ('登录信息', {'fields': ('last_login_at', 'last_login_platform', 'is_active', 'is_deleted')}),
        ('时间', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login_at')
    filter_horizontal = ()


@admin.register(AuthLoginTicket)
class AuthLoginTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'status', 'user', 'expires_at', 'confirmed_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('ticket', 'scan_openid', 'scan_unionid')
    readonly_fields = ('created_at',)

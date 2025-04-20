from django.contrib import admin
from .models import UserRole, UserPermission, AdminUser, ActivityLog

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'created_at', 'updated_at')
    search_fields = ('name', 'codename', 'description')

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'created_at')
    list_filter = ('is_active', 'role')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('permissions',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('created_at',)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from userauths.models import User, ContactUs, Profile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'make_staff', 'remove_staff']
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"
    
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)
    make_staff.short_description = "Make selected users staff members"
    
    def remove_staff(self, request, queryset):
        queryset.update(is_staff=False)
    remove_staff.short_description = "Remove staff status from selected users"

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'verified')
    list_filter = ('verified',)
    search_fields = ('user__username', 'user__email', 'phone', 'full_name')
    list_per_page = 25
    ordering = ('-user__date_joined',)
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'full_name', 'phone', 'bio', 'image')
        }),
        (_('Status'), {
            'fields': ('verified',),
        }),
    )
    
    actions = ['export_profiles', 'verify_profiles', 'unverify_profiles']
    
    def export_profiles(self, request, queryset):
        # Add export functionality if needed
        pass
    export_profiles.short_description = "Export selected profiles"
    
    def verify_profiles(self, request, queryset):
        queryset.update(verified=True)
    verify_profiles.short_description = "Verify selected profiles"
    
    def unverify_profiles(self, request, queryset):
        queryset.update(verified=False)
    unverify_profiles.short_description = "Unverify selected profiles"

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject')
    search_fields = ('full_name', 'email', 'phone', 'subject', 'message')
    list_per_page = 25
    ordering = ('-id',)
    
    fieldsets = (
        (_('Contact Information'), {
            'fields': ('full_name', 'email', 'phone', 'subject', 'message')
        }),
    )
    
    actions = ['export_contacts']
    
    def export_contacts(self, request, queryset):
        # Add export functionality if needed
        pass
    export_contacts.short_description = "Export selected contacts"

# تسجيل النماذج
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactUs, ContactUsAdmin)

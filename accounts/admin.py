from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('-created_at',)
    list_per_page = 25
    fieldsets = UserAdmin.fieldsets + (
        ('Restaurant Info', {'fields': ('role', 'phone', 'address', 'profile_image')}),
    )
    readonly_fields = ('created_at',)

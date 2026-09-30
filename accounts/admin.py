from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'is_active', 'date_joined']
    list_filter = ['rol', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Rol y Permisos', {'fields': ('rol', 'telefono')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol y Permisos', {'fields': ('rol',)}),
    )
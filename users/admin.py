from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'year_of_study', 'is_approved', 'pending_approval')
    list_filter = ('role', 'year_of_study', 'is_approved')
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {'fields': ('year_of_study',)}),
        ('Role & Approval', {'fields': ('role', 'is_approved', 'pending_approval')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + ('User type',{'fields':('role','year_of_study')}),
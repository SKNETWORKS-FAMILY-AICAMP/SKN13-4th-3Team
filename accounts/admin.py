from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

# User Admin 커스텀
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    fieldsets = (
        ('계정 정보', {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('first_name', 'last_name', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요 날짜', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'image']

# Admin에 등록
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
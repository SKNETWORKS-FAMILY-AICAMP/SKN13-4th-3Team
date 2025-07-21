from django.contrib import admin
from .models import User, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# User 모델용 Admin
class CustomUserAdmin(BaseUserAdmin): 
    list_display = ["username", "first_name", "last_name", "email"]
    add_fieldsets = (
        ("인증정보", {"fields": ("username", "password1", "password2")}),
        ("개인정보", {"fields": ("first_name", "last_name", "email")}),
    )
    fieldsets = (
        ("인증정보", {"fields": ("username", "password")}),
        ("개인정보", {"fields": ("first_name", "last_name", "email")}),
        ("권한", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

# Profile 모델용 Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "image"]

# Django Admin 등록
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)

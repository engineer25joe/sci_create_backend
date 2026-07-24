from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.identity.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("email", "display_name", "is_email_verified", "is_active", "date_joined")
    search_fields = ("email", "display_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("SCI CREATE profile", {"fields": ("display_name", "preferred_language", "is_email_verified")}),
    )
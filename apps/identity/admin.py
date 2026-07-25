from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.identity.models import Organization, User, Workspace, WorkspaceMember


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("email", "display_name", "is_email_verified", "is_active", "date_joined")
    search_fields = ("email", "display_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("SCI CREATE profile", {"fields": ("display_name", "preferred_language", "is_email_verified")}),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "is_active", "created_at")
    search_fields = ("name", "slug")


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "owner_user", "organization", "is_default", "created_at")
    search_fields = ("name",)


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role", "invited_by", "created_at")
    list_filter = ("role",)
    search_fields = ("user__email", "workspace__name")

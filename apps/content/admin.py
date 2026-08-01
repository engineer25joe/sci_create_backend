from django.contrib import admin

from apps.content.models import Content, ContentAnalytics, ContentVersion


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "content_type", "workspace", "created_by", "is_favorite", "created_at")
    list_filter = ("content_type", "is_favorite", "is_archived")
    search_fields = ("title", "body")


@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    list_display = ("content", "created_by", "change_note", "created_at")
    readonly_fields = [f.name for f in ContentVersion._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("content", "views", "likes", "comments", "shares", "last_updated")

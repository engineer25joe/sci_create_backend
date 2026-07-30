from django.contrib import admin

from apps.community.models import CommunityComment, CommunityPost, CommunityPostLike


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("author", "like_count", "is_hidden", "created_at")
    list_filter = ("is_hidden",)
    search_fields = ("body", "author__email")


@admin.register(CommunityComment)
class CommunityCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "is_hidden", "created_at")
    list_filter = ("is_hidden",)


admin.site.register(CommunityPostLike)

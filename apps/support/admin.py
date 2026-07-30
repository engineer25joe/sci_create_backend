from django.contrib import admin

from apps.support.models import FeatureRequest, FeatureRequestUpvote, SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("subject", "user__email")


@admin.register(FeatureRequest)
class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "upvote_count", "created_at")
    list_filter = ("status",)
    search_fields = ("title",)


admin.site.register(FeatureRequestUpvote)

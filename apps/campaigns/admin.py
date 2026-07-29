from django.contrib import admin

from apps.campaigns.models import Campaign, CampaignContent


class CampaignContentInline(admin.TabularInline):
    model = CampaignContent
    extra = 0


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "status", "start_date", "end_date", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)
    inlines = [CampaignContentInline]

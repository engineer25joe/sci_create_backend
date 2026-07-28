from django.contrib import admin

from apps.ai_core.models import AIProviderStatus


@admin.register(AIProviderStatus)
class AIProviderStatusAdmin(admin.ModelAdmin):
    list_display = ("display_name", "name", "is_manually_disabled", "updated_at")
    list_editable = ("is_manually_disabled",)

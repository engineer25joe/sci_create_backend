from django.contrib import admin

from apps.planner.models import CalendarEntry


@admin.register(CalendarEntry)
class CalendarEntryAdmin(admin.ModelAdmin):
    list_display = ("content", "workspace", "scheduled_for", "status", "target_platform")
    list_filter = ("status", "target_platform")
    search_fields = ("content__title",)

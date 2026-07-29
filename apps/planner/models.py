import uuid

from django.conf import settings
from django.db import models


class CalendarEntryStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    SCHEDULED = "scheduled", "Scheduled"
    PUBLISHED = "published", "Published"
    CANCELLED = "cancelled", "Cancelled"


class CalendarEntry(models.Model):
    """
    A single planned/scheduled piece of content on the calendar.
    Publishing integrations (Phase 2) will read from this to actually
    push content to social platforms at scheduled_for.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "identity.Workspace", on_delete=models.CASCADE, related_name="calendar_entries"
    )
    content = models.ForeignKey(
        "content.Content", on_delete=models.CASCADE, related_name="calendar_entries"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=CalendarEntryStatus.choices, default=CalendarEntryStatus.PLANNED)
    target_platform = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_for"]

    def __str__(self):
        return f"{self.content} @ {self.scheduled_for}"

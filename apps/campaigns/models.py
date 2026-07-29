import uuid

from django.conf import settings
from django.db import models


class CampaignStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    COMPLETED = "completed", "Completed"


class Campaign(models.Model):
    """
    Groups related Content items and CalendarEntry schedules under one
    goal-driven initiative (e.g. "Q3 Product Launch"). AI campaign
    generation (Phase 2/3) will create Content items linked here.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "identity.Workspace", on_delete=models.CASCADE, related_name="campaigns"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    name = models.CharField(max_length=200)
    goal = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class CampaignContent(models.Model):
    """Links Content items to a Campaign (many-to-many with metadata)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_content")
    content = models.ForeignKey("content.Content", on_delete=models.CASCADE, related_name="campaigns")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("campaign", "content")

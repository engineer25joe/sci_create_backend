import uuid

from django.conf import settings
from django.db import models


class NotificationCategory(models.TextChoices):
    BILLING = "billing", "Billing"
    SECURITY = "security", "Security"
    AI_ACTIVITY = "ai_activity", "AI Activity"
    PUBLISHING = "publishing", "Publishing"
    TEAM = "team", "Team Collaboration"
    PRODUCT = "product", "Product Updates"


class Notification(models.Model):
    """
    In-app notification. Push/email/SMS delivery (Phase 2) will read
    from these plus NotificationPreference to decide channel and
    whether to send at all.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    workspace = models.ForeignKey(
        "identity.Workspace", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    category = models.CharField(max_length=30, choices=NotificationCategory.choices)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.user.email}"


class NotificationPreference(models.Model):
    """One row per user per category - lets users mute non-critical
    categories while security/billing stay forced-on at the app layer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    category = models.CharField(max_length=30, choices=NotificationCategory.choices)
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "category")

import uuid

from django.conf import settings
from django.db import models


class TicketStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_tickets")
    workspace = models.ForeignKey(
        "identity.Workspace", on_delete=models.SET_NULL, null=True, blank=True, related_name="support_tickets"
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject


class FeatureRequestStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    PLANNED = "planned", "Planned"
    IN_PROGRESS = "in_progress", "In Progress"
    SHIPPED = "shipped", "Shipped"
    DECLINED = "declined", "Declined"


class FeatureRequest(models.Model):
    """Community feature request hub - users submit and upvote ideas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="feature_requests"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=FeatureRequestStatus.choices, default=FeatureRequestStatus.SUBMITTED)
    upvote_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-upvote_count", "-created_at"]

    def __str__(self):
        return self.title


class FeatureRequestUpvote(models.Model):
    """Prevents a user from upvoting the same request twice."""

    feature_request = models.ForeignKey(FeatureRequest, on_delete=models.CASCADE, related_name="upvotes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("feature_request", "user")

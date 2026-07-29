import uuid

from django.conf import settings
from django.db import models


class ContentType(models.TextChoices):
    CAPTION = "caption", "Caption"
    BLOG_POST = "blog_post", "Blog Post"
    SOCIAL_POST = "social_post", "Social Media Post"
    EMAIL = "email", "Email Newsletter"
    AD_COPY = "ad_copy", "Ad Copy"
    VIDEO_SCRIPT = "video_script", "Video Script"
    OTHER = "other", "Other"


class Content(models.Model):
    """
    The universal resource model referenced throughout our architecture:
    tags, favorites, folders, soft-delete (via deleted_at/is_archived)
    all live here so search and trash/archive work the same way across
    every content type. parent_content lets one item spawn derived
    pieces (e.g. a blog post -> an Instagram caption) while preserving
    lineage.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "identity.Workspace", on_delete=models.CASCADE, related_name="content_items"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="content_created"
    )
    content_type = models.CharField(max_length=30, choices=ContentType.choices)
    title = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)

    parent_content = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="derived_content"
    )

    ai_provider_used = models.CharField(max_length=50, blank=True)
    ai_request = models.ForeignKey(
        "ai_core.AIRequestLog", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    tags = models.JSONField(default=list, blank=True)
    is_favorite = models.BooleanField(default=False)

    deleted_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def soft_delete(self):
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def __str__(self):
        return self.title or f"{self.content_type} ({self.id})"


class ContentVersion(models.Model):
    """
    Snapshot of Content.body at a point in time - created whenever
    content is edited (AI-improved or manually), so users can browse,
    compare, and restore previous versions per our architecture.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="versions")
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    change_note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Version of {self.content_id} @ {self.created_at}"

import uuid

from django.conf import settings
from django.db import models


class CommunityPost(models.Model):
    """
    A post shared to the SCI CREATE Community Feed - one of our v1
    publishing targets. Can optionally originate from a Content item
    (shared from a user's own workspace) or be written directly.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_posts"
    )
    source_content = models.ForeignKey(
        "content.Content", on_delete=models.SET_NULL, null=True, blank=True, related_name="community_posts"
    )
    body = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False, help_text="Moderation - hide without deleting.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author.email} @ {self.created_at}"


class CommunityPostLike(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")


class CommunityComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    body = models.TextField()
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

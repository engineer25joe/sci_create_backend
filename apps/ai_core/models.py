from django.db import models


class AIProviderStatus(models.Model):
    """
    One row per provider (gemini, openai, anthropic, ...). Availability
    is auto-detected from whether the provider's API key is set in the
    environment, but an admin can manually force a provider to show as
    "coming soon" even if a key exists (e.g. temporarily disabling one
    during an incident) via is_manually_disabled.
    """

    name = models.SlugField(primary_key=True, max_length=50)
    display_name = models.CharField(max_length=100)
    is_manually_disabled = models.BooleanField(
        default=False, help_text="Force this provider to show as 'coming soon' regardless of API key status."
    )
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name


class AIRequestLog(models.Model):
    """
    One row per AI generation request. Minimal for now (Milestone 2) -
    this is what AI Analytics (tracking cost, latency, success/failure
    rate) will build on top of later.
    """

    id = models.BigAutoField(primary_key=True)
    workspace = models.ForeignKey("identity.Workspace", on_delete=models.CASCADE, related_name="ai_requests")
    user = models.ForeignKey("identity.User", on_delete=models.SET_NULL, null=True, related_name="ai_requests")
    provider_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100, blank=True)
    prompt = models.TextField()
    response_text = models.TextField(blank=True)
    was_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

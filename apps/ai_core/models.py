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

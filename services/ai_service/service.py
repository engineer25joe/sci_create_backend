"""
ai_service - the only place that decides which AI provider handles a
request and orchestrates the call. Views never call provider adapters
directly.
"""
from apps.ai_core.models import AIProviderStatus, AIRequestLog
from libs.ai_abstraction.base import (
    AIRequestSpec,
    AIResponseResult,
    ProviderNotConfiguredError,
)
from libs.ai_abstraction.base import provider_registry as _default_registry


class ProviderUnavailableError(Exception):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        super().__init__(f"{provider_name} is not currently available.")


def is_provider_available(provider_name: str, *, registry=None) -> bool:
    """
    A provider is available only if BOTH:
      - it's registered and reports is_configured() == True (has an API key)
      - it hasn't been manually disabled by an admin (AIProviderStatus)
    """
    registry = registry or _default_registry
    try:
        adapter = registry.get(provider_name)
    except KeyError:
        return False

    if not adapter.is_configured():
        return False

    status = AIProviderStatus.objects.filter(name=provider_name).first()
    if status and status.is_manually_disabled:
        return False

    return True


def generate_content(*, workspace, user, provider_name: str, prompt: str, registry=None) -> AIResponseResult:
    """
    Main entry point views call. Logs every attempt (success or
    failure) to AIRequestLog for visibility, per our architecture's
    AI Analytics plans.
    """
    registry = registry or _default_registry

    if not is_provider_available(provider_name, registry=registry):
        raise ProviderUnavailableError(provider_name)

    adapter = registry.get(provider_name)
    spec = AIRequestSpec(prompt=prompt)

    log = AIRequestLog.objects.create(
        workspace=workspace,
        user=user,
        provider_name=provider_name,
        prompt=prompt,
        was_successful=False,
    )

    try:
        result = adapter.generate(spec)
    except ProviderNotConfiguredError:
        log.error_message = "Provider not configured."
        log.save(update_fields=["error_message"])
        raise ProviderUnavailableError(provider_name)
    except Exception as exc:  # noqa: BLE001
        log.error_message = str(exc)
        log.save(update_fields=["error_message"])
        raise

    log.model_name = result.model_name
    log.response_text = result.text
    log.was_successful = True
    log.save(update_fields=["model_name", "response_text", "was_successful"])

    return result

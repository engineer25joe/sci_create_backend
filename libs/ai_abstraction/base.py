"""
AI Abstraction Layer - common interface every AI provider adapter must
implement, per our architecture. Nothing outside this package should
ever import a provider-specific SDK or call a provider's API directly.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIRequestSpec:
    prompt: str
    max_output_tokens: int = 1024


@dataclass
class AIResponseResult:
    text: str
    provider_name: str
    model_name: str
    raw_response: dict


class ProviderNotConfiguredError(Exception):
    """Raised when a provider is selected but has no API key set - the
    caller should treat this the same as 'coming soon' in the admin."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        super().__init__(f"{provider_name} is not configured (missing API key).")


class AIProviderAdapter(ABC):
    name: str

    @abstractmethod
    def is_configured(self) -> bool:
        """True if this provider has the API key/config it needs to
        actually make requests."""

    @abstractmethod
    def generate(self, spec: AIRequestSpec) -> AIResponseResult:
        """Makes the actual HTTP call to the provider and returns a
        normalized result. Raises ProviderNotConfiguredError if
        is_configured() would have returned False."""


class ProviderRegistry:
    """Maps provider name -> adapter instance."""

    def __init__(self):
        self._adapters: dict[str, AIProviderAdapter] = {}

    def register(self, adapter: AIProviderAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> AIProviderAdapter:
        return self._adapters[name]

    def all(self):
        return self._adapters.values()


provider_registry = ProviderRegistry()

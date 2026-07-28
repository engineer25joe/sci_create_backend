"""
Anthropic adapter - calls the Messages API directly over HTTP, no SDK
required.
"""
import os

import requests

from libs.ai_abstraction.base import (
    AIProviderAdapter,
    AIRequestSpec,
    AIResponseResult,
    ProviderNotConfiguredError,
)

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


class AnthropicAdapter(AIProviderAdapter):
    name = "anthropic"
    model = "claude-3-5-haiku-20241022"

    def is_configured(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def generate(self, spec: AIRequestSpec) -> AIResponseResult:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderNotConfiguredError(self.name)

        headers = {
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
        }
        payload = {
            "model": self.model,
            "max_tokens": spec.max_output_tokens,
            "messages": [{"role": "user", "content": spec.prompt}],
        }

        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        text = data["content"][0]["text"]

        return AIResponseResult(
            text=text,
            provider_name=self.name,
            model_name=self.model,
            raw_response=data,
        )

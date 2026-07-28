"""
OpenAI adapter - calls the Chat Completions API directly over HTTP,
no SDK required.
"""
import os

import requests

from libs.ai_abstraction.base import (
    AIProviderAdapter,
    AIRequestSpec,
    AIResponseResult,
    ProviderNotConfiguredError,
)

API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIAdapter(AIProviderAdapter):
    name = "openai"
    model = "gpt-4o-mini"

    def is_configured(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def generate(self, spec: AIRequestSpec) -> AIResponseResult:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ProviderNotConfiguredError(self.name)

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": spec.prompt}],
            "max_tokens": spec.max_output_tokens,
        }

        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        text = data["choices"][0]["message"]["content"]

        return AIResponseResult(
            text=text,
            provider_name=self.name,
            model_name=self.model,
            raw_response=data,
        )

"""
Llama adapter - via Together AI's hosting (OpenAI-compatible API).
Meta doesn't offer a direct hosted API for Llama models, so this uses
a well-known third-party host. The interface stays identical to every
other adapter, so swapping hosts later (Groq, Fireworks, etc.) is a
one-file change.
"""
import os

import requests

from libs.ai_abstraction.base import (
    AIProviderAdapter,
    AIRequestSpec,
    AIResponseResult,
    ProviderNotConfiguredError,
)

API_URL = "https://api.together.xyz/v1/chat/completions"


class LlamaAdapter(AIProviderAdapter):
    name = "llama"
    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    def is_configured(self) -> bool:
        return bool(os.environ.get("TOGETHER_API_KEY"))

    def generate(self, spec: AIRequestSpec) -> AIResponseResult:
        api_key = os.environ.get("TOGETHER_API_KEY")
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

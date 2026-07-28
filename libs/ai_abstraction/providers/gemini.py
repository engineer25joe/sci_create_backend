"""
Gemini adapter - calls Google's Generative Language API directly over
HTTP, no SDK required. This avoids the Rust/maturin build issues we
hit trying to install google-generativeai on Termux.
"""
import os

import requests

from libs.ai_abstraction.base import (
    AIProviderAdapter,
    AIRequestSpec,
    AIResponseResult,
    ProviderNotConfiguredError,
)

API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
)


class GeminiAdapter(AIProviderAdapter):
    name = "gemini"
    model = "gemini-1.5-flash"

    def is_configured(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY"))

    def generate(self, spec: AIRequestSpec) -> AIResponseResult:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ProviderNotConfiguredError(self.name)

        url = API_URL_TEMPLATE.format(model=self.model, api_key=api_key)
        payload = {
            "contents": [{"parts": [{"text": spec.prompt}]}],
            "generationConfig": {"maxOutputTokens": spec.max_output_tokens},
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return AIResponseResult(
            text=text,
            provider_name=self.name,
            model_name=self.model,
            raw_response=data,
        )

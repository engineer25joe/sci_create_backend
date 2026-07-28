from django.apps import AppConfig


class AIAbstractionConfig(AppConfig):
    name = "libs.ai_abstraction"
    label = "ai_abstraction"

    def ready(self):
        from libs.ai_abstraction.base import provider_registry
        from libs.ai_abstraction.providers.anthropic_provider import AnthropicAdapter
        from libs.ai_abstraction.providers.cohere_provider import CohereAdapter
        from libs.ai_abstraction.providers.deepseek import DeepSeekAdapter
        from libs.ai_abstraction.providers.gemini import GeminiAdapter
        from libs.ai_abstraction.providers.grok import GrokAdapter
        from libs.ai_abstraction.providers.llama import LlamaAdapter
        from libs.ai_abstraction.providers.mistral import MistralAdapter
        from libs.ai_abstraction.providers.openai_provider import OpenAIAdapter
        from libs.ai_abstraction.providers.perplexity import PerplexityAdapter

        provider_registry.register(GeminiAdapter())
        provider_registry.register(OpenAIAdapter())
        provider_registry.register(AnthropicAdapter())
        provider_registry.register(GrokAdapter())
        provider_registry.register(MistralAdapter())
        provider_registry.register(DeepSeekAdapter())
        provider_registry.register(CohereAdapter())
        provider_registry.register(PerplexityAdapter())
        provider_registry.register(LlamaAdapter())

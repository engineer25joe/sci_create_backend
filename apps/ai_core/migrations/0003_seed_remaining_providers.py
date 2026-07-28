from django.db import migrations


def seed_providers(apps, schema_editor):
    AIProviderStatus = apps.get_model("ai_core", "AIProviderStatus")
    providers = [
        ("grok", "Grok (xAI)"),
        ("mistral", "Mistral"),
        ("deepseek", "DeepSeek"),
        ("cohere", "Cohere"),
        ("perplexity", "Perplexity"),
        ("llama", "Llama (via Together AI)"),
    ]
    for name, display_name in providers:
        AIProviderStatus.objects.get_or_create(name=name, defaults={"display_name": display_name})


def remove_providers(apps, schema_editor):
    AIProviderStatus = apps.get_model("ai_core", "AIProviderStatus")
    AIProviderStatus.objects.filter(
        name__in=["grok", "mistral", "deepseek", "cohere", "perplexity", "llama"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0002_seed_provider_statuses"),
    ]

    operations = [
        migrations.RunPython(seed_providers, remove_providers),
    ]

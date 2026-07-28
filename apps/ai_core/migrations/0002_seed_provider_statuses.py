from django.db import migrations


def seed_providers(apps, schema_editor):
    AIProviderStatus = apps.get_model("ai_core", "AIProviderStatus")
    providers = [
        ("gemini", "Google Gemini"),
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic Claude"),
    ]
    for name, display_name in providers:
        AIProviderStatus.objects.get_or_create(name=name, defaults={"display_name": display_name})


def remove_providers(apps, schema_editor):
    AIProviderStatus = apps.get_model("ai_core", "AIProviderStatus")
    AIProviderStatus.objects.filter(name__in=["gemini", "openai", "anthropic"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_providers, remove_providers),
    ]

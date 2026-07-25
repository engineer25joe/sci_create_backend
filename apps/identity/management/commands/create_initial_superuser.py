"""
Creates a superuser from environment variables if one doesn't already
exist. Safe to run on every deploy (idempotent) - this is how we get
an admin account onto Render's free tier, which has no shell access.

Reads:
  DJANGO_SUPERUSER_EMAIL
  DJANGO_SUPERUSER_PASSWORD
Both must be set as Render environment variables - never committed.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser from DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD env vars if none exists."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD not set - skipping."
            ))
            return

        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} already exists - skipping."))
            return

        User.objects.create_superuser(email=email, username=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser {email} created."))

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model, keyed by UUID and authenticating by email
    instead of username. username is kept (Django's AbstractUser
    requires it internally) but auto-generated and not used to log in.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, blank=True)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    preferred_language = models.CharField(max_length=10, default="en")
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"user_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
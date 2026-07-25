import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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


class Organization(models.Model):
    """
    An organization owns one or more Workspaces once Phase 2 team
    collaboration is enabled. Created now so Workspace.organization has
    somewhere to point without a later schema change.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owned_organizations")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Workspace(models.Model):
    """
    Every tenant-scoped resource in the platform will eventually point
    here. A workspace is either:
      - personal: owner_user set, organization is null
      - organizational: organization set, owner_user is null
    Never both, never neither.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    owner_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="personal_workspaces"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True, related_name="workspaces"
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if bool(self.owner_user) == bool(self.organization):
            raise ValidationError(
                "Workspace must have exactly one of owner_user or organization set."
            )

    @property
    def is_personal(self) -> bool:
        return self.owner_user_id is not None

    def __str__(self):
        return self.name
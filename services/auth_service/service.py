"""
auth_service - the only place authentication/authorization business
logic is allowed to live (View -> Service -> Model, per our architecture).
Views call these functions; they never create Users/Workspaces directly.
"""
from django.db import transaction

from apps.identity.models import User, Workspace


class RegistrationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@transaction.atomic
def register_user(*, email: str, password: str, display_name: str = "") -> User:
    if User.objects.filter(email__iexact=email).exists():
        raise RegistrationError("An account with this email already exists.")

    user = User.objects.create_user(
        email=email.lower(),
        username=email.lower(),
        password=password,
        display_name=display_name,
    )

    Workspace.objects.create(
        name=f"{display_name or user.email}'s Workspace",
        owner_user=user,
        is_default=True,
    )

    return user

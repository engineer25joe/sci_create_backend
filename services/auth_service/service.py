"""
auth_service - the only place authentication/authorization business
logic is allowed to live (View -> Service -> Model, per our architecture).
Views call these functions; they never create/query Users, Workspaces,
or WorkspaceMembers directly for anything auth-related.
"""
from django.db import transaction

from apps.identity.models import Role, User, Workspace, WorkspaceMember

# Roles ranked by privilege - used for simple "does this role meet the
# bar" checks. Fine-grained per-permission-string checks (e.g.
# "content.publish", "billing.manage") can replace this ranking later
# without changing any code that calls user_has_permission().
_ROLE_RANK = {Role.MEMBER: 0, Role.EDITOR: 1, Role.MANAGER: 2, Role.ADMIN: 3}


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


def user_can_access_workspace(user: User, workspace: Workspace) -> bool:
    """True if the user may see/use this workspace at all (read access).
    Write/manage access is a separate, stricter check via
    user_has_permission()."""
    if workspace.is_personal:
        return workspace.owner_user_id == user.id
    return WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()


def user_role_in_workspace(user: User, workspace: Workspace) -> str | None:
    if workspace.is_personal:
        return Role.ADMIN if workspace.owner_user_id == user.id else None
    membership = WorkspaceMember.objects.filter(workspace=workspace, user=user).first()
    return membership.role if membership else None


def user_has_permission(user: User, workspace: Workspace, permission: str) -> bool:
    """
    `permission` is a dotted string like "content.write" or
    "billing.manage" - callers should already use this style even
    though, for now, it's mapped onto simple role ranks. When a real
    per-permission model replaces this, call sites don't change.
    """
    role = user_role_in_workspace(user, workspace)
    if role is None:
        return False
    if permission.endswith(".manage"):
        return _ROLE_RANK[role] >= _ROLE_RANK[Role.ADMIN]
    if permission.endswith(".write") or permission.endswith(".publish"):
        return _ROLE_RANK[role] >= _ROLE_RANK[Role.EDITOR]
    return True


def default_workspace_for(user: User) -> Workspace:
    workspace = Workspace.objects.filter(owner_user=user, is_default=True).first()
    if workspace is None:
        raise ValueError("User has no default workspace.")
    return workspace


@transaction.atomic
def create_organization(*, owner: User, name: str, slug: str) -> Workspace:
    """
    Creates an Organization + its Workspace, and makes the creator an
    admin WorkspaceMember. Returns the Workspace (not the Organization)
    since that's what callers actually scope resources to.
    """
    from apps.identity.models import Organization

    if Organization.objects.filter(slug=slug).exists():
        raise ValueError(f"An organization with slug '{slug}' already exists.")

    org = Organization.objects.create(name=name, slug=slug, owner=owner)
    workspace = Workspace.objects.create(name=name, organization=org)
    WorkspaceMember.objects.create(workspace=workspace, user=owner, role=Role.ADMIN)

    return workspace

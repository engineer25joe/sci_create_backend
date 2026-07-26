import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_creates_user_and_default_workspace():
    client = APIClient()
    response = client.post(
        "/api/v1/identity/register/",
        {"email": "pytest-user@scicreate.com", "password": "a-strong-password-1", "display_name": "Pytest User"},
        format="json",
    )
    assert response.status_code == 201
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_duplicate_email_registration_rejected():
    client = APIClient()
    payload = {"email": "dupe@scicreate.com", "password": "a-strong-password-1"}
    first = client.post("/api/v1/identity/register/", payload, format="json")
    assert first.status_code == 201

    second = client.post("/api/v1/identity/register/", payload, format="json")
    assert second.status_code == 400


@pytest.mark.django_db
def test_login_and_me_endpoint():
    client = APIClient()
    client.post(
        "/api/v1/identity/register/",
        {"email": "login-test@scicreate.com", "password": "a-strong-password-1"},
        format="json",
    )

    login_response = client.post(
        "/api/v1/identity/login/",
        {"email": "login-test@scicreate.com", "password": "a-strong-password-1"},
        format="json",
    )
    assert login_response.status_code == 200
    access_token = login_response.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    me_response = client.get("/api/v1/identity/me/")
    assert me_response.status_code == 200
    assert me_response.data["user"]["email"] == "login-test@scicreate.com"
    assert len(me_response.data["workspaces"]) == 1


@pytest.mark.django_db
def test_health_endpoint():
    client = APIClient()
    response = client.get("/api/v1/system/health/")
    assert response.status_code == 200
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_owner_has_admin_role_in_personal_workspace():
    from apps.identity.models import Role, User, Workspace
    from services.auth_service.service import user_has_permission, user_role_in_workspace

    user = User.objects.create_user(email="owner@scicreate.com", username="owner@scicreate.com", password="a-strong-password-1")
    workspace = Workspace.objects.create(name="Owner's Workspace", owner_user=user, is_default=True)

    assert user_role_in_workspace(user, workspace) == Role.ADMIN
    assert user_has_permission(user, workspace, "billing.manage") is True


@pytest.mark.django_db
def test_member_role_cannot_manage_billing():
    from apps.identity.models import Organization, Role, User, Workspace, WorkspaceMember
    from services.auth_service.service import user_has_permission

    owner = User.objects.create_user(email="org-owner@scicreate.com", username="org-owner@scicreate.com", password="a-strong-password-1")
    member = User.objects.create_user(email="org-member@scicreate.com", username="org-member@scicreate.com", password="a-strong-password-1")

    org = Organization.objects.create(name="Test Org", slug="test-org", owner=owner)
    workspace = Workspace.objects.create(name="Test Org Workspace", organization=org)
    WorkspaceMember.objects.create(workspace=workspace, user=member, role=Role.MEMBER)

    assert user_has_permission(member, workspace, "billing.manage") is False
    assert user_has_permission(member, workspace, "content.read") is True


@pytest.mark.django_db
def test_create_organization_creates_workspace_and_admin_membership():
    from apps.identity.models import Role, User, WorkspaceMember
    from services.auth_service.service import create_organization

    owner = User.objects.create_user(
        email="org-founder@scicreate.com", username="org-founder@scicreate.com", password="a-strong-password-1"
    )

    workspace = create_organization(owner=owner, name="Acme Agency", slug="acme-agency")

    assert workspace.organization is not None
    assert workspace.organization.name == "Acme Agency"
    assert workspace.organization.slug == "acme-agency"

    membership = WorkspaceMember.objects.get(workspace=workspace, user=owner)
    assert membership.role == Role.ADMIN


@pytest.mark.django_db
def test_create_organization_rejects_duplicate_slug():
    from apps.identity.models import User
    from services.auth_service.service import create_organization

    owner = User.objects.create_user(
        email="dup-org-owner@scicreate.com", username="dup-org-owner@scicreate.com", password="a-strong-password-1"
    )

    create_organization(owner=owner, name="First Org", slug="shared-slug")

    with pytest.raises(ValueError):
        create_organization(owner=owner, name="Second Org", slug="shared-slug")

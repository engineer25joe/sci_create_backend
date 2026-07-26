from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.identity.views import (
    BrandProfileView,
    CreateOrganizationView,
    InviteMemberView,
    MeView,
    RegisterView,
    WorkspaceMembersView,
)

app_name = "identity"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("organizations/", CreateOrganizationView.as_view(), name="create_organization"),
    path("workspaces/<uuid:workspace_id>/invite/", InviteMemberView.as_view(), name="invite_member"),
    path("workspaces/<uuid:workspace_id>/members/", WorkspaceMembersView.as_view(), name="workspace_members"),
    path("workspaces/<uuid:workspace_id>/brand-profile/", BrandProfileView.as_view(), name="brand_profile"),
]

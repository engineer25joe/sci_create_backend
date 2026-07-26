from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.identity.models import BrandProfile, Workspace
from apps.identity.serializers import (
    BrandProfileSerializer,
    CreateOrganizationSerializer,
    InviteMemberSerializer,
    RegisterSerializer,
    UserSerializer,
    WorkspaceMemberSerializer,
    WorkspaceSerializer,
)
from services.auth_service.service import (
    PermissionDeniedError,
    RegistrationError,
    create_organization,
    invite_member,
    register_user,
    user_can_access_workspace,
)


class RegisterView(APIView):
    """POST /api/v1/identity/register/"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = register_user(**serializer.validated_data)
        except RegistrationError as exc:
            return Response({"error": exc.message}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """GET /api/v1/identity/me/ - current user + their workspaces."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspaces = Workspace.objects.filter(owner_user=request.user) | Workspace.objects.filter(
            members__user=request.user
        )
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "workspaces": WorkspaceSerializer(workspaces.distinct(), many=True).data,
            }
        )


class CreateOrganizationView(APIView):
    """POST /api/v1/identity/organizations/ - creates an org + workspace,
    makes the requesting user its admin."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            workspace = create_organization(owner=request.user, **serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(WorkspaceSerializer(workspace).data, status=status.HTTP_201_CREATED)


class InviteMemberView(APIView):
    """POST /api/v1/identity/workspaces/<workspace_id>/invite/"""

    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = invite_member(inviter=request.user, workspace=workspace, **serializer.validated_data)
        except PermissionDeniedError as exc:
            return Response({"error": exc.message}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(WorkspaceMemberSerializer(membership).data, status=status.HTTP_201_CREATED)


class WorkspaceMembersView(APIView):
    """GET /api/v1/identity/workspaces/<workspace_id>/members/"""

    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user_can_access_workspace(request.user, workspace):
            return Response({"error": "You do not have access to this workspace."}, status=status.HTTP_403_FORBIDDEN)

        members = workspace.members.select_related("user").all()
        return Response(WorkspaceMemberSerializer(members, many=True).data)


class BrandProfileView(APIView):
    """
    GET  /api/v1/identity/workspaces/<workspace_id>/brand-profile/
    PATCH /api/v1/identity/workspaces/<workspace_id>/brand-profile/
    """

    permission_classes = [IsAuthenticated]

    def _get_workspace_or_404(self, workspace_id, request):
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return None, Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_workspace(request.user, workspace):
            return None, Response(
                {"error": "You do not have access to this workspace."}, status=status.HTTP_403_FORBIDDEN
            )
        return workspace, None

    def get(self, request, workspace_id):
        workspace, error_response = self._get_workspace_or_404(workspace_id, request)
        if error_response:
            return error_response

        profile, _ = BrandProfile.objects.get_or_create(workspace=workspace)
        return Response(BrandProfileSerializer(profile).data)

    def patch(self, request, workspace_id):
        workspace, error_response = self._get_workspace_or_404(workspace_id, request)
        if error_response:
            return error_response

        profile, _ = BrandProfile.objects.get_or_create(workspace=workspace)
        serializer = BrandProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

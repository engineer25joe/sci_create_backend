from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.identity.models import Workspace
from apps.identity.serializers import (
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

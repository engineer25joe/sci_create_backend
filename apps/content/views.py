from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Content, ContentVersion
from apps.content.serializers import ContentSerializer, ContentVersionSerializer
from apps.identity.models import Workspace
from services.auth_service.service import user_can_access_workspace


class ContentListCreateView(APIView):
    """
    GET  /api/v1/content/?workspace_id=<uuid> - list content in a workspace
    POST /api/v1/content/ - create new content
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_workspace(request.user, workspace):
            return Response({"error": "You do not have access to this workspace."}, status=status.HTTP_403_FORBIDDEN)

        items = Content.objects.filter(workspace=workspace, deleted_at__isnull=True)
        return Response(ContentSerializer(items, many=True).data)

    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_workspace(request.user, workspace):
            return Response({"error": "You do not have access to this workspace."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.save(workspace=workspace, created_by=request.user)

        return Response(ContentSerializer(content).data, status=status.HTTP_201_CREATED)


class ContentDetailView(APIView):
    """
    GET   /api/v1/content/<content_id>/
    PATCH /api/v1/content/<content_id>/ - creates a ContentVersion snapshot first
    """

    permission_classes = [IsAuthenticated]

    def _get_content_or_404(self, content_id, request):
        content = Content.objects.filter(id=content_id, deleted_at__isnull=True).first()
        if content is None:
            return None, Response({"error": "Content not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_workspace(request.user, content.workspace):
            return None, Response(
                {"error": "You do not have access to this content."}, status=status.HTTP_403_FORBIDDEN
            )
        return content, None

    def get(self, request, content_id):
        content, error_response = self._get_content_or_404(content_id, request)
        if error_response:
            return error_response
        return Response(ContentSerializer(content).data)

    def patch(self, request, content_id):
        content, error_response = self._get_content_or_404(content_id, request)
        if error_response:
            return error_response

        if "body" in request.data and request.data["body"] != content.body:
            ContentVersion.objects.create(
                content=content, body=content.body, created_by=request.user, change_note="Edited"
            )

        serializer = ContentSerializer(content, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ContentVersionListView(APIView):
    """GET /api/v1/content/<content_id>/versions/"""

    permission_classes = [IsAuthenticated]

    def get(self, request, content_id):
        content = Content.objects.filter(id=content_id, deleted_at__isnull=True).first()
        if content is None:
            return Response({"error": "Content not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user_can_access_workspace(request.user, content.workspace):
            return Response({"error": "You do not have access to this content."}, status=status.HTTP_403_FORBIDDEN)

        versions = content.versions.all()
        return Response(ContentVersionSerializer(versions, many=True).data)

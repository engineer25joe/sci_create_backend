from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_core.serializers import GenerateContentSerializer
from apps.identity.models import Workspace
from services.ai_service.service import ProviderUnavailableError, generate_content
from services.auth_service.service import user_can_access_workspace


class GenerateContentView(APIView):
    """POST /api/v1/ai/generate/"""

    permission_classes = [IsAuthenticated]
    throttle_scope = "ai"

    def post(self, request):
        serializer = GenerateContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        workspace = Workspace.objects.filter(id=data["workspace_id"]).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user_can_access_workspace(request.user, workspace):
            return Response({"error": "You do not have access to this workspace."}, status=status.HTTP_403_FORBIDDEN)

        try:
            result = generate_content(
                workspace=workspace,
                user=request.user,
                provider_name=data["provider"],
                prompt=data["prompt"],
            )
        except ProviderUnavailableError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "text": result.text,
                "provider": result.provider_name,
                "model": result.model_name,
            }
        )

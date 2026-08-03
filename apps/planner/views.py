from datetime import datetime, time, timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import Workspace
from apps.planner.models import CalendarEntry
from services.auth_service.service import user_can_access_workspace


class TodayPlannerView(APIView):
    """GET /api/v1/planner/today/?workspace_id=<uuid>"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=404)
        if not user_can_access_workspace(request.user, workspace):
            return Response({"error": "You do not have access to this workspace."}, status=403)

        now = timezone.now()
        start_of_day = timezone.make_aware(datetime.combine(now.date(), time.min))
        end_of_day = start_of_day + timedelta(days=1)

        entries = CalendarEntry.objects.filter(
            workspace=workspace, scheduled_for__gte=start_of_day, scheduled_for__lt=end_of_day
        ).select_related("content")

        return Response(
            [
                {
                    "id": str(entry.id),
                    "scheduled_for": entry.scheduled_for.isoformat(),
                    "status": entry.status,
                    "target_platform": entry.target_platform,
                    "content_title": entry.content.title or "Untitled",
                }
                for entry in entries
            ]
        )

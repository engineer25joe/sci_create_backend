from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import Workspace
from services.auth_service.service import user_can_access_workspace
from services.billing_service.service import get_or_create_wallet


class CreditBalanceView(APIView):
    """GET /api/v1/billing/credits/?workspace_id=<uuid>"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            return Response({"error": "Workspace not found."}, status=404)
        if not user_can_access_workspace(request.user, workspace):
            return Response({"error": "You do not have access to this workspace."}, status=403)

        wallet = get_or_create_wallet(workspace)
        subscription = getattr(workspace, "subscription", None)

        return Response(
            {
                "balance": wallet.balance,
                "plan_name": subscription.plan.name if subscription else "Free Plan",
                "plan_tier": subscription.plan.tier if subscription else "free",
            }
        )

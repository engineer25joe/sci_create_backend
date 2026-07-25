from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    GET /api/v1/system/health/

    Confirms the backend is up and can reach its database. This is
    the first thing to check after any deploy, especially since we
    can't easily "watch logs" the way a desktop dev would.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        db_ok = True
        db_error = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as exc:  # noqa: BLE001
            db_ok = False
            db_error = str(exc)

        status_code = 200 if db_ok else 503
        return Response(
            {
                "status": "ok" if db_ok else "degraded",
                "checks": {"database": {"ok": db_ok, "error": db_error}},
            },
            status=status_code,
        )

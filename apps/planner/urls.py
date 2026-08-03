from django.urls import path

from apps.planner.views import TodayPlannerView

app_name = "planner"

urlpatterns = [
    path("today/", TodayPlannerView.as_view(), name="today"),
]

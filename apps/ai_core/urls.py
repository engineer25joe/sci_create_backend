from django.urls import path

from apps.ai_core.views import GenerateContentView

app_name = "ai_core"

urlpatterns = [
    path("generate/", GenerateContentView.as_view(), name="generate"),
]

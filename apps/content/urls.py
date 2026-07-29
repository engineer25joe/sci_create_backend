from django.urls import path

from apps.content.views import (
    ContentDetailView,
    ContentListCreateView,
    ContentVersionListView,
)

app_name = "content"

urlpatterns = [
    path("", ContentListCreateView.as_view(), name="content_list_create"),
    path("<uuid:content_id>/", ContentDetailView.as_view(), name="content_detail"),
    path("<uuid:content_id>/versions/", ContentVersionListView.as_view(), name="content_versions"),
]

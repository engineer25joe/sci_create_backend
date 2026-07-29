"""
URL configuration for SCI CREATE backend.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/identity/', include('apps.identity.urls')),
    path('api/v1/system/', include('apps.system.urls')),
    path('api/v1/ai/', include('apps.ai_core.urls')),
]

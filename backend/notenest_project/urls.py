"""
URL configuration for notenest_project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('core.urls')),
]

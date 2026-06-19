"""
URL configuration for notenest_project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        "status": "ok",
        "project": "NoteNest API",
        "version": "1.0",
        "endpoints": {
            "semesters": "/api/admin/semesters/",
            "faculty": "/api/admin/faculty/",
            "questions": "/api/admin/questions/",
            "login": "/api/admin/auth/login/",
            "signup": "/api/admin/auth/signup/",
            "admin_panel": "/admin/",
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/admin/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

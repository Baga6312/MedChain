from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


handler500 = "config.error_views.json_server_error"
handler404 = "config.error_views.json_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("healthcare.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if not settings.DEBUG:
        urlpatterns.append(
            path(
                "media/<path:path>",
                serve,
                {"document_root": settings.MEDIA_ROOT},
            )
        )

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.cache import add_never_cache_headers, patch_vary_headers

from apps.core.models import SiteConfiguration

RETRY_AFTER_SECONDS = 3600


class MaintenanceModeMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
    ) -> None:
        self.get_response = get_response
        self.admin_path = reverse("admin:index")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._is_admin_request(request):
            return self.get_response(request)

        user = getattr(request, "user", None)

        if user is not None and user.is_authenticated and (user.is_staff or user.is_superuser):
            return self.get_response(request)

        configuration = (
            SiteConfiguration.objects.only(
                "maintenance_mode_enabled",
                "maintenance_title",
                "maintenance_message",
            )
            .filter(pk=1)
            .first()
        )

        if configuration is None or not configuration.maintenance_mode_enabled:
            return self.get_response(request)

        response = render(
            request,
            "core/maintenance.html",
            {
                "maintenance_title": configuration.maintenance_title,
                "maintenance_message": configuration.maintenance_message,
            },
            status=503,
        )

        response.headers["Retry-After"] = str(RETRY_AFTER_SECONDS)

        add_never_cache_headers(response)
        patch_vary_headers(response, ("Cookie",))

        return response

    def _is_admin_request(self, request: HttpRequest) -> bool:
        admin_path_without_slash = self.admin_path.rstrip("/")

        return request.path == admin_path_without_slash or request.path.startswith(self.admin_path)

from django.contrib import admin
from django.http import HttpRequest

from core.models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fields = [
        "maintenance_mode_enabled",
        "maintenance_title",
        "maintenance_message",
        "updated_at",
    ]
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        if SiteConfiguration.objects.exists():
            return False

        return super().has_add_permission(request)

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: SiteConfiguration | None = None,
    ) -> bool:
        return False

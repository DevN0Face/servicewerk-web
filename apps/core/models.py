# core/models

from django.db import models


class SiteConfiguration(models.Model):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )

    maintenance_mode_enabled = models.BooleanField(
        default=False,
        verbose_name="Wartungsmodus aktiviert",
    )

    maintenance_title = models.CharField(
        max_length=200,
        default="Wir sind bald wieder für Sie da.",
        verbose_name="Überschrift der Wartungsseite",
    )

    maintenance_message = models.TextField(
        default=("Unsere Website wird derzeit gewartet. Bitte versuchen Sie es später erneut."),
        verbose_name="Text der Wartungsseite",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Zuletzt geändert",
    )

    class Meta:
        verbose_name = "Website-Konfiguration"
        verbose_name_plural = "Website-Konfiguration"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(id=1), name="core_site_configuration_singleton"
            ),
        ]

    def __str__(self) -> str:
        return "Website-Konfiguration"

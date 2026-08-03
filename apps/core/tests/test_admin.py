from django.contrib import admin
from django.test import RequestFactory
from django.urls import reverse

from apps.core.admin import SiteConfigurationAdmin
from apps.core.models import SiteConfiguration


def test_site_configuration_can_only_be_added_once(
    db,
    django_user_model,
):
    superuser = django_user_model.objects.create_superuser(
        username="admin-user",
        email="admin@example.com",
        password="test-password",
    )

    request = RequestFactory().get(
        reverse("admin:core_siteconfiguration_changelist"),
    )
    request.user = superuser

    model_admin = SiteConfigurationAdmin(
        SiteConfiguration,
        admin.site,
    )

    assert model_admin.has_add_permission(request) is True

    SiteConfiguration.objects.create()

    assert model_admin.has_add_permission(request) is False


def test_site_configuration_cannot_be_deleted(
    db,
    django_user_model,
):
    superuser = django_user_model.objects.create_superuser(
        username="admin-user",
        email="admin@example.com",
        password="test-password",
    )
    configuration = SiteConfiguration.objects.create()

    request = RequestFactory().get(
        reverse(
            "admin:core_siteconfiguration_change",
            args=(configuration.pk,),
        ),
    )
    request.user = superuser

    model_admin = SiteConfigurationAdmin(
        SiteConfiguration,
        admin.site,
    )

    assert (
        model_admin.has_delete_permission(
            request,
            configuration,
        )
        is False
    )

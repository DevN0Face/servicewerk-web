import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from core.models import SiteConfiguration


def test_disabled_maintenance_mode_allows_normal_website(client, db):
    SiteConfiguration.objects.create(
        maintenance_mode_enabled=False,
    )

    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Außenreinigung" in response.content.decode()


def test_enabled_maintenance_mode_returns_503_for_anonymous_user(
    client,
    db,
):
    SiteConfiguration.objects.create(
        maintenance_mode_enabled=True,
        maintenance_title="Test-Wartungsarbeiten",
        maintenance_message="Die Website ist vorübergehend nicht erreichbar.",
    )

    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 503
    assert "Test-Wartungsarbeiten" in content
    assert "Die Website ist vorübergehend nicht erreichbar." in content

    assert response.headers["Retry-After"] == "3600"

    cache_control = response.headers["Cache-Control"]
    assert "no-cache" in cache_control
    assert "no-store" in cache_control
    assert "private" in cache_control

    assert "Cookie" in response.headers["Vary"]

def test_admin_login_remains_reachable_during_maintenance(client, db):
    SiteConfiguration.objects.create(
        maintenance_mode_enabled=True,
    )

    response = client.get(reverse("admin:login"))

    assert response.status_code == 200
    assert response.status_code != 503


def test_staff_user_can_access_normal_website_during_maintenance(
    client,
    django_user_model,
):
    staff_user = django_user_model.objects.create_user(
        username="staff-user",
        password="test-password",
        is_staff=True,
    )
    SiteConfiguration.objects.create(
        maintenance_mode_enabled=True,
    )
    client.force_login(staff_user)

    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Außenreinigung" in response.content.decode()


def test_authenticated_non_staff_user_still_sees_maintenance_page(
    client,
    django_user_model,
):
    regular_user = django_user_model.objects.create_user(
        username="regular-user",
        password="test-password",
    )
    SiteConfiguration.objects.create(
        maintenance_mode_enabled=True,
    )
    client.force_login(regular_user)

    response = client.get(reverse("core:home"))

    assert response.status_code == 503

def test_missing_configuration_allows_normal_website(client, db):
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Außenreinigung" in response.content.decode()

def test_database_rejects_additional_site_configuration(db):
    SiteConfiguration.objects.create()

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            SiteConfiguration.objects.create(id=2)

    assert SiteConfiguration.objects.count() == 1

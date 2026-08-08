import pytest
from django.test import override_settings


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_custom_404_page_is_rendered(client):
    response = client.get("/this-page-does-not-exist/")

    assert response.status_code == 404
    assert any(
        template.name == "errors/404.html" for template in response.templates if template.name
    )

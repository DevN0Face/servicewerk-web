from django.urls import reverse


def test_homepage_is_reachable(client):
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Außenreinigung" in response.content.decode()

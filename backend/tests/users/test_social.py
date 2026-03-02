import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_social_connections_page(auth_client):
    response = auth_client.get(reverse("socialaccount_connections"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_social_connections_redirects_unauthenticated(client):
    response = client.get(reverse("socialaccount_connections"))
    assert response.status_code == 302

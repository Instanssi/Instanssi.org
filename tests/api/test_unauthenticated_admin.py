import pytest

# Nor logged in. Should receive UNAUTHENTICATED 401 everywhere.


@pytest.mark.django_db
def test_unauthenticated_admin_events(api_client):
    url = "/api/v1/admin/events/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.delete(url).status_code == 401
    assert api_client.patch(url).status_code == 401
    assert api_client.put(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_unauthenticated_admin_compos(api_client):
    url = "/api/v1/admin/compos/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.delete(url).status_code == 401
    assert api_client.patch(url).status_code == 401
    assert api_client.put(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_unauthenticated_admin_compo_entries(api_client):
    url = "/api/v1/admin/compo_entries/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.delete(url).status_code == 401
    assert api_client.patch(url).status_code == 401
    assert api_client.put(url).status_code == 401
    assert api_client.options(url).status_code == 401

import pytest


@pytest.mark.django_db
def test_authenticated_admin_events(staff_api_client):
    url = "/api/v1/admin/events/"
    assert staff_api_client.get(url).status_code == 200
    assert staff_api_client.post(url).status_code == 405
    assert staff_api_client.delete(url).status_code == 405
    assert staff_api_client.patch(url).status_code == 405
    assert staff_api_client.put(url).status_code == 405
    assert staff_api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_authenticated_admin_compos(staff_api_client):
    url = "/api/v1/admin/compos/"
    assert staff_api_client.get(url).status_code == 200
    assert staff_api_client.post(url).status_code == 405
    assert staff_api_client.delete(url).status_code == 405
    assert staff_api_client.patch(url).status_code == 405
    assert staff_api_client.put(url).status_code == 405
    assert staff_api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_authenticated_admin_compo_entries(staff_api_client):
    url = "/api/v1/admin/compo_entries/"
    assert staff_api_client.get(url).status_code == 200
    assert staff_api_client.post(url).status_code == 405
    assert staff_api_client.delete(url).status_code == 405
    assert staff_api_client.patch(url).status_code == 405
    assert staff_api_client.put(url).status_code == 405
    assert staff_api_client.options(url).status_code == 200

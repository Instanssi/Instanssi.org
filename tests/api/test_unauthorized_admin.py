import pytest

# Logging in as normal user. Should receive UNAUTHORIZED 403 everywhere.


@pytest.mark.django_db
def test_unauthenticated_admin_events(user_api_client):
    url = "/api/v1/admin/events/"
    assert user_api_client.get(url).status_code == 403
    assert user_api_client.post(url).status_code == 403
    assert user_api_client.delete(url).status_code == 403
    assert user_api_client.patch(url).status_code == 403
    assert user_api_client.put(url).status_code == 403
    assert user_api_client.options(url).status_code == 403


@pytest.mark.django_db
def test_unauthenticated_admin_compos(user_api_client):
    url = "/api/v1/admin/compos/"
    assert user_api_client.get(url).status_code == 403
    assert user_api_client.post(url).status_code == 403
    assert user_api_client.delete(url).status_code == 403
    assert user_api_client.patch(url).status_code == 403
    assert user_api_client.put(url).status_code == 403
    assert user_api_client.options(url).status_code == 403


@pytest.mark.django_db
def test_unauthenticated_admin_compo_entries(user_api_client):
    url = "/api/v1/admin/compo_entries/"
    assert user_api_client.get(url).status_code == 403
    assert user_api_client.post(url).status_code == 403
    assert user_api_client.delete(url).status_code == 403
    assert user_api_client.patch(url).status_code == 403
    assert user_api_client.put(url).status_code == 403
    assert user_api_client.options(url).status_code == 403

import pytest

BASE_URL = "/api/v1/admin/events/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("DELETE", 401),
        ("PATCH", 401),
        ("PUT", 401),
        ("HEAD", 401),
        ("OPTIONS", 401),
    ],
)
def test_unauthenticated_admin_events(api_client, method, status):
    assert api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("DELETE", 403),
        ("PATCH", 403),
        ("PUT", 403),
        ("HEAD", 403),
        ("OPTIONS", 403),
    ],
)
def test_unauthorized_admin_events(user_api_client, method, status):
    assert user_api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),
        ("POST", 405),
        ("DELETE", 405),
        ("PATCH", 405),
        ("PUT", 405),
        ("HEAD", 200),
        ("OPTIONS", 200),
    ],
)
def test_authenticated_admin_events(staff_api_client, method, status):
    assert staff_api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
def test_admin_events_list_response(staff_api_client, event):
    req = staff_api_client.get(BASE_URL)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": event.id,
            "name": "Instanssi 2025",
            "date": "2025-01-15",
            "archived": False,
            "mainurl": "http://localhost:8000/2025/",
        }
    ]


@pytest.mark.django_db
def test_admin_events_detail_response(staff_api_client, event):
    req = staff_api_client.get(f"{BASE_URL}{event.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": event.id,
        "name": "Instanssi 2025",
        "date": "2025-01-15",
        "archived": False,
        "mainurl": "http://localhost:8000/2025/",
    }

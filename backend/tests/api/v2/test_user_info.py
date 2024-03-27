import pytest

BASE_URL = "/api/v2/user_info/"


@pytest.mark.django_db
def test_unauthenticated_user_info(api_client):
    """Test unauthenticated access (Not logged in)"""
    assert api_client.get(BASE_URL).status_code == 401


@pytest.mark.django_db
def test_authenticated_user_info(auth_client, base_user):
    """Test authenticated access, and make sure serializer spits out correct looking stuff."""
    response = auth_client.get(BASE_URL)
    assert response.status_code == 200
    assert response.data == [
        {
            "id": base_user.id,
            "first_name": base_user.first_name,
            "last_name": base_user.last_name,
            "email": base_user.email,
            "user_permissions": [],
            "is_superuser": base_user.is_superuser,
        }
    ]

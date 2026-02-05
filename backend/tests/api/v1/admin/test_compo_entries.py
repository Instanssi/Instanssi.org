import pytest
from freezegun import freeze_time

from tests.api.helpers import file_url

BASE_URL = "/api/v1/admin/compo_entries/"
FROZEN_TIME = "2025-01-15T12:00:00Z"


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
def test_unauthenticated_admin_compo_entries(api_client, method, status):
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
def test_unauthorized_admin_compo_entries(user_api_client, method, status):
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
def test_authenticated_admin_compo_entries(staff_api_client, method, status):
    assert staff_api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_admin_compo_entries_list_response(staff_api_client, editable_compo_entry):
    req = staff_api_client.get(BASE_URL)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": editable_compo_entry.id,
            "user": editable_compo_entry.user_id,
            "compo": editable_compo_entry.compo_id,
            "name": "Test Entry",
            "description": "An editable test entry",
            "creator": "Test Creator",
            "platform": "Commodore 64",
            "entryfile_url": file_url(editable_compo_entry.entryfile),
            "sourcefile_url": file_url(editable_compo_entry.sourcefile),
            "imagefile_original_url": file_url(editable_compo_entry.imagefile_original),
            "imagefile_thumbnail_url": file_url(editable_compo_entry.imagefile_thumbnail),
            "imagefile_medium_url": file_url(editable_compo_entry.imagefile_medium),
            "youtube_url": None,
            "disqualified": False,
            "disqualified_reason": "",
            "score": 0.0,
            "rank": 1,
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_admin_compo_entries_detail_response(staff_api_client, editable_compo_entry):
    req = staff_api_client.get(f"{BASE_URL}{editable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": editable_compo_entry.id,
        "user": editable_compo_entry.user_id,
        "compo": editable_compo_entry.compo_id,
        "name": "Test Entry",
        "description": "An editable test entry",
        "creator": "Test Creator",
        "platform": "Commodore 64",
        "entryfile_url": file_url(editable_compo_entry.entryfile),
        "sourcefile_url": file_url(editable_compo_entry.sourcefile),
        "imagefile_original_url": file_url(editable_compo_entry.imagefile_original),
        "imagefile_thumbnail_url": file_url(editable_compo_entry.imagefile_thumbnail),
        "imagefile_medium_url": file_url(editable_compo_entry.imagefile_medium),
        "youtube_url": None,
        "disqualified": False,
        "disqualified_reason": "",
        "score": 0.0,
        "rank": 1,
    }

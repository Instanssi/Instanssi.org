import pytest

BASE_URL = "/api/v2/user_compo_entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 401),
        (True, "GET", 401),
        (False, "POST", 401),
        (True, "DELETE", 401),
        (True, "PATCH", 401),
        (True, "PUT", 401),
    ],
)
def test_unauthenticated_blog_entries(api_client, obj, method, status):
    """Test unauthenticated access (Not logged in)"""
    url = f"{BASE_URL}1/" if obj else BASE_URL
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_post_user_compo_entry(auth_client, open_compo, entry_zip, source_zip, image_png):
    req = auth_client.post(
        BASE_URL,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Awesome test entry description",
            "creator": "Test Creator 2000",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_post_user_compo_entry_with_uppercase_ext(auth_client, open_compo, entry_zip, source_zip, image_png):
    entry_zip.name = "entry_file.ZIP"  # UPPERCASE EXTS
    source_zip.name = "source_file.ZIP"
    image_png.name = "image.PNG"
    req = auth_client.post(
        BASE_URL,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Potentially problematic test entry",
            "creator": "8.3 For Life",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_get_user_compo_entries(auth_client, editable_compo_entry):
    assert auth_client.get(BASE_URL).status_code == 200


@pytest.mark.django_db
def test_get_user_compo_entry(auth_client, votable_compo_entry):
    req = auth_client.get(f"{BASE_URL}{votable_compo_entry.id}/")
    assert req.status_code == 200
    data = req.data
    assert data["id"] == votable_compo_entry.id
    assert data["compo"] == votable_compo_entry.compo_id
    assert data["name"] == votable_compo_entry.name
    assert data["description"] == votable_compo_entry.description
    assert data["creator"] == votable_compo_entry.creator
    assert data["platform"] == votable_compo_entry.platform
    assert data["entry_file_url"] is not None
    assert data["source_file_url"] is not None
    assert data["image_file_original_url"] is not None
    assert data["image_file_thumbnail_url"] is not None
    assert data["image_file_medium_url"] is not None
    assert data["disqualified"] == votable_compo_entry.disqualified
    assert data["disqualified_reason"] == votable_compo_entry.disqualified_reason


@pytest.mark.django_db
def test_patch_user_compo_entry(auth_client, votable_compo_entry):
    instance_url = f"{BASE_URL}{votable_compo_entry.id}/"
    req = auth_client.patch(
        instance_url,
        format="multipart",
        data={
            "id": 3,  # Should not change
            "name": "Test Entry 2",  # Should change
            "description": "Awesome test entry description 2",  # Should change
            "creator": "Test Creator 3000",  # Should change
            "imagefile_original": "",
        },
    )
    assert req.status_code == 200

    # Make sure entry changed
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    data = req.data

    assert data["id"] == votable_compo_entry.id
    assert data["compo"] == votable_compo_entry.compo_id
    assert data["name"] == "Test Entry 2"
    assert data["description"] == "Awesome test entry description 2"
    assert data["creator"] == "Test Creator 3000"
    assert data["platform"] == votable_compo_entry.platform
    assert data["entry_file_url"] is not None
    assert data["source_file_url"] is not None
    assert data["image_file_original_url"] is None
    assert data["image_file_thumbnail_url"] is None
    assert data["image_file_medium_url"] is None
    assert data["disqualified"] == votable_compo_entry.disqualified
    assert data["disqualified_reason"] == votable_compo_entry.disqualified_reason


@pytest.mark.django_db
def test_put_user_compo_entry(auth_client, votable_compo_entry, entry_zip2, source_zip2, image_png2):
    instance_url = f"{BASE_URL}{votable_compo_entry.id}/"

    req = auth_client.put(
        instance_url,
        format="multipart",
        data={
            "compo": votable_compo_entry.compo_id,
            "name": "Test Entry",
            "description": "Awesome test entry description",
            "creator": "Test Creator 3000",
            "platform": "Linux (Ubuntu 18.04)",
            "entryfile": entry_zip2,
            "imagefile_original": image_png2,
            "sourcefile": source_zip2,
        },
    )
    assert req.status_code == 200

    # Make sure entry changed
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    data = req.data

    assert data["id"] == votable_compo_entry.id
    assert data["compo"] == votable_compo_entry.compo_id
    assert data["name"] == "Test Entry"
    assert data["description"] == "Awesome test entry description"
    assert data["creator"] == "Test Creator 3000"
    assert data["platform"] == "Linux (Ubuntu 18.04)"
    assert data["entry_file_url"] is not None
    assert data["source_file_url"] is not None
    assert data["image_file_original_url"] is not None
    assert data["image_file_thumbnail_url"] is not None
    assert data["image_file_medium_url"] is not None
    assert data["disqualified"] == votable_compo_entry.disqualified
    assert data["disqualified_reason"] == votable_compo_entry.disqualified_reason


@pytest.mark.django_db
def test_delete_user_compo_entry(auth_client, editable_compo_entry):
    instance_url = f"{BASE_URL}{editable_compo_entry.id}/"
    assert auth_client.delete(instance_url).status_code == 204
    assert auth_client.get(instance_url).status_code == 404

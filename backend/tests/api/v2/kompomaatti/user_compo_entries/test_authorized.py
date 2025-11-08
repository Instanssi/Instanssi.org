import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/entries/"


@pytest.mark.django_db
def test_post_user_compo_entry(auth_client, open_compo, entry_zip, source_zip, image_png):
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
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
    base_url = get_base_url(open_compo.event_id)
    entry_zip.name = "entry_file.ZIP"  # UPPERCASE EXTS
    source_zip.name = "source_file.ZIP"
    image_png.name = "image.PNG"
    req = auth_client.post(
        base_url,
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
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    assert auth_client.get(base_url).status_code == 200


@pytest.mark.django_db
def test_get_user_compo_entry(auth_client, votable_compo_entry):
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = auth_client.get(f"{base_url}{votable_compo_entry.id}/")
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
def test_patch_user_compo_entry(auth_client, editable_compo_entry):
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{editable_compo_entry.id}/"
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

    assert data["id"] == editable_compo_entry.id
    assert data["compo"] == editable_compo_entry.compo_id
    assert data["name"] == "Test Entry 2"
    assert data["description"] == "Awesome test entry description 2"
    assert data["creator"] == "Test Creator 3000"
    assert data["platform"] == editable_compo_entry.platform
    assert data["entry_file_url"] is not None
    assert data["source_file_url"] is not None
    assert data["image_file_original_url"] is None
    assert data["image_file_thumbnail_url"] is None
    assert data["image_file_medium_url"] is None
    assert data["disqualified"] is None
    assert data["disqualified_reason"] is None


@pytest.mark.django_db
def test_put_user_compo_entry(auth_client, editable_compo_entry, entry_zip2, source_zip2, image_png2):
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{editable_compo_entry.id}/"

    req = auth_client.put(
        instance_url,
        format="multipart",
        data={
            "compo": editable_compo_entry.compo_id,
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

    assert data["id"] == editable_compo_entry.id
    assert data["compo"] == editable_compo_entry.compo_id
    assert data["name"] == "Test Entry"
    assert data["description"] == "Awesome test entry description"
    assert data["creator"] == "Test Creator 3000"
    assert data["platform"] == "Linux (Ubuntu 18.04)"
    assert data["entry_file_url"] is not None
    assert data["source_file_url"] is not None
    assert data["image_file_original_url"] is not None
    assert data["image_file_thumbnail_url"] is not None
    assert data["image_file_medium_url"] is not None
    assert data["disqualified"] is None
    assert data["disqualified_reason"] is None


@pytest.mark.django_db
def test_delete_user_compo_entry(auth_client, editable_compo_entry):
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{editable_compo_entry.id}/"
    assert auth_client.delete(instance_url).status_code == 204
    assert auth_client.get(instance_url).status_code == 404


@pytest.mark.django_db
def test_cannot_create_entry_in_closed_compo(auth_client, closed_compo, entry_zip, source_zip, image_png):
    """Test that entries cannot be created after adding deadline has passed"""
    base_url = get_base_url(closed_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": closed_compo.id,
            "name": "Test Entry",
            "description": "Should not work",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "adding time has ended" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_edit_entry_after_deadline(auth_client, votable_compo_entry):
    """Test that entries cannot be edited after editing deadline has passed"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{votable_compo_entry.id}/"
    req = auth_client.patch(
        instance_url,
        format="multipart",
        data={
            "name": "Should not work",
        },
    )
    assert req.status_code == 400
    assert "edit time has ended" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_delete_entry_after_deadline(auth_client, votable_compo_entry):
    """Test that entries cannot be deleted after editing deadline has passed"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{votable_compo_entry.id}/"
    req = auth_client.delete(instance_url)
    assert req.status_code == 400
    assert "edit time has ended" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_create_entry_in_inactive_compo(auth_client, open_compo, entry_zip, source_zip, image_png):
    """Test that entries cannot be created in inactive compos"""
    # Make the compo inactive
    open_compo.active = False
    open_compo.save()

    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should not work",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "not active" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_edit_entry_in_inactive_compo(auth_client, editable_compo_entry):
    """Test that entries cannot be edited when compo becomes inactive"""
    # Make the compo inactive
    editable_compo_entry.compo.active = False
    editable_compo_entry.compo.save()

    base_url = get_base_url(editable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{editable_compo_entry.id}/"
    req = auth_client.patch(
        instance_url,
        format="multipart",
        data={
            "name": "Should not work",
        },
    )
    # Entry is filtered out by get_queryset() when compo is inactive, resulting in 404
    assert req.status_code == 404


@pytest.mark.django_db
def test_cannot_delete_entry_in_inactive_compo(auth_client, editable_compo_entry):
    """Test that entries cannot be deleted when compo becomes inactive"""
    # Make the compo inactive
    editable_compo_entry.compo.active = False
    editable_compo_entry.compo.save()

    base_url = get_base_url(editable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{editable_compo_entry.id}/"
    req = auth_client.delete(instance_url)
    # Entry is filtered out by get_queryset() when compo is inactive, resulting in 404
    assert req.status_code == 404

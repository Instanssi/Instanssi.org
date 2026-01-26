import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/entries/"


@pytest.mark.django_db
def test_get_admin_compo_entries_list(staff_api_client, editable_compo_entry, votable_compo_entry):
    """Test retrieving list of all compo entries as staff"""
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 2


@pytest.mark.django_db
def test_get_admin_compo_entry_detail(staff_api_client, votable_compo_entry):
    """Test retrieving a single compo entry as staff"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = staff_api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    data = req.data
    assert data["id"] == votable_compo_entry.id
    assert data["compo"] == votable_compo_entry.compo_id
    assert data["user"] == votable_compo_entry.user_id
    assert data["name"] == votable_compo_entry.name
    assert data["description"] == votable_compo_entry.description
    assert data["creator"] == votable_compo_entry.creator
    assert data["platform"] == votable_compo_entry.platform
    assert data["entryfile_url"] is not None
    assert data["sourcefile_url"] is not None
    assert data["imagefile_original_url"] is not None
    assert data["imagefile_thumbnail_url"] is not None
    assert data["imagefile_medium_url"] is not None
    assert data["disqualified"] == votable_compo_entry.disqualified
    assert data["disqualified_reason"] == votable_compo_entry.disqualified_reason
    assert "rank" in data
    assert "score" in data


@pytest.mark.django_db
def test_post_admin_compo_entry(staff_api_client, open_compo, base_user, entry_zip, source_zip, image_png):
    """Test creating a new compo entry via admin API"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.post(
        base_url,
        format="multipart",
        data={
            "user": base_user.id,
            "compo": open_compo.id,
            "name": "Admin Created Entry",
            "description": "Entry created by admin",
            "creator": "Admin Creator",
            "platform": "Any",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201
    assert req.data["name"] == "Admin Created Entry"
    assert req.data["creator"] == "Admin Creator"
    assert req.data["user"] == base_user.id


@pytest.mark.django_db
def test_patch_admin_compo_entry(staff_api_client, votable_compo_entry):
    """Test partially updating a compo entry via admin API"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{votable_compo_entry.id}/"
    req = staff_api_client.patch(
        instance_url,
        format="multipart",
        data={
            "name": "Updated Entry Name",
            "description": "Updated description",
            "disqualified": True,
            "disqualified_reason": "Admin disqualification test",
        },
    )
    assert req.status_code == 200

    # Verify changes
    req = staff_api_client.get(instance_url)
    assert req.status_code == 200
    data = req.data
    assert data["name"] == "Updated Entry Name"
    assert data["description"] == "Updated description"
    assert data["disqualified"] is True
    assert data["disqualified_reason"] == "Admin disqualification test"


@pytest.mark.django_db
def test_put_admin_compo_entry(staff_api_client, votable_compo_entry, entry_zip2, source_zip2, image_png2):
    """Test full replacement of a compo entry via admin API"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{votable_compo_entry.id}/"

    req = staff_api_client.put(
        instance_url,
        format="multipart",
        data={
            "user": votable_compo_entry.user_id,
            "compo": votable_compo_entry.compo_id,
            "name": "Completely Replaced Entry",
            "description": "Full replacement test",
            "creator": "New Creator Name",
            "platform": "New Platform",
            "entryfile": entry_zip2,
            "imagefile_original": image_png2,
            "sourcefile": source_zip2,
        },
    )
    assert req.status_code == 200

    # Verify changes
    req = staff_api_client.get(instance_url)
    assert req.status_code == 200
    data = req.data
    assert data["name"] == "Completely Replaced Entry"
    assert data["creator"] == "New Creator Name"
    assert data["platform"] == "New Platform"


@pytest.mark.django_db
def test_delete_admin_compo_entry(staff_api_client, editable_compo_entry):
    """Test deleting a compo entry via admin API"""
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{editable_compo_entry.id}/"
    assert staff_api_client.delete(instance_url).status_code == 204
    assert staff_api_client.get(instance_url).status_code == 404


@pytest.mark.django_db
def test_entries_filter_by_compo(
    staff_api_client, open_compo, votable_compo, editable_compo_entry, votable_compo_entry
):
    """Test filtering entries by compo"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.get(base_url, {"compo": open_compo.id})
    assert req.status_code == 200
    assert len(req.data) == 1
    assert req.data[0]["compo"] == open_compo.id


@pytest.mark.django_db
def test_entries_filter_by_user(staff_api_client, base_user, editable_compo_entry):
    """Test filtering entries by user"""
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    req = staff_api_client.get(base_url, {"user": base_user.id})
    assert req.status_code == 200
    assert len(req.data) >= 1
    for entry in req.data:
        assert entry["user"] == base_user.id


@pytest.mark.django_db
def test_filter_by_disqualified(staff_api_client, votable_compo_entry):
    """Test filtering entries by disqualified status"""
    # First disqualify an entry
    votable_compo_entry.disqualified = True
    votable_compo_entry.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = staff_api_client.get(base_url, {"disqualified": "true"})
    assert req.status_code == 200
    assert len(req.data) >= 1
    for entry in req.data:
        assert entry["disqualified"] is True


@pytest.mark.django_db
def test_ordering_by_id(staff_api_client, editable_compo_entry, votable_compo_entry):
    """Test ordering entries by id"""
    base_url = get_base_url(editable_compo_entry.compo.event_id)
    req = staff_api_client.get(base_url, {"ordering": "-id"})
    assert req.status_code == 200
    assert len(req.data) >= 2
    ids = [entry["id"] for entry in req.data]
    assert ids == sorted(ids, reverse=True)


@pytest.mark.django_db
def test_admin_can_set_archive_score_and_rank(staff_api_client, votable_compo_entry):
    """Test that admin can set archive_score and archive_rank"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    instance_url = f"{base_url}{votable_compo_entry.id}/"
    req = staff_api_client.patch(
        instance_url,
        format="multipart",
        data={
            "archive_score": 42.5,
            "archive_rank": 3,
        },
    )
    assert req.status_code == 200
    assert req.data["archive_score"] == 42.5
    assert req.data["archive_rank"] == 3


@pytest.mark.django_db
def test_staff_can_always_see_entry_score_rank(staff_api_client, votable_compo_entry):
    """Test that staff users can always see score/rank regardless of show_voting_results"""
    votable_compo_entry.compo.show_voting_results = False
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = staff_api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["score"] is not None
    assert req.data["rank"] is not None


@pytest.mark.django_db
def test_entry_includes_alternate_files(staff_api_client, votable_alternate_entry_file):
    """Test that entry response includes alternate_files with format and url"""
    entry = votable_alternate_entry_file.entry
    base_url = get_base_url(entry.compo.event_id)
    req = staff_api_client.get(f"{base_url}{entry.id}/")
    assert req.status_code == 200
    assert "alternate_files" in req.data
    assert len(req.data["alternate_files"]) == 1
    alt_file = req.data["alternate_files"][0]
    assert "format" in alt_file
    assert "url" in alt_file
    assert alt_file["format"] == "audio/webm;codecs=opus"
    assert alt_file["url"].endswith(".webm")


@pytest.mark.django_db
def test_entry_without_alternate_files_returns_empty_list(staff_api_client, votable_compo_entry):
    """Test that entry without alternate files returns empty list"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = staff_api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert "alternate_files" in req.data
    assert req.data["alternate_files"] == []

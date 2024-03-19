import pytest


@pytest.mark.django_db
def test_auth_events(auth_client):
    url = "/api/v1/events/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_competitions(auth_client):
    url = "/api/v1/competitions/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_competition_participations(auth_client):
    url = "/api/v1/competition_participations/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_competition_participation_ok(auth_client, competition):
    url = "/api/v1/user_participations/"
    req = auth_client.post(
        url,
        data={
            "competition": competition.id,
            "participant_name": "Pertti Partisipantti",
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_auth_competition_participation_fail(auth_client, competition_participation, competition):
    url = "/api/v1/user_participations/"

    # Try to make an overlapping participation, should fail
    req = auth_client.post(
        url,
        data={
            "competition": competition.id,
            "participant_name": competition_participation.participant_name,
        },
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Olet jo osallistunut tähän kilpailuun"]}


@pytest.mark.django_db
def test_auth_competition_participation_get(auth_client, competition_participation):
    url = "/api/v1/user_participations/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": competition_participation.id,
            "competition": competition_participation.competition_id,
            "participant_name": competition_participation.participant_name,
        }
    ]


@pytest.mark.django_db
def test_auth_competition_participation_options(auth_client):
    url = "/api/v1/user_participations/"
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_competition_participation_instance_patch(auth_client, competition_participation):
    instance_url = "/api/v1/user_participations/{}/".format(competition_participation.id)
    req = auth_client.patch(
        instance_url,
        data={
            "id": competition_participation.id + 1,  # Should not affect anything
            "participant_name": "Pertti Perusjuntti",  # Should change
        },
    )
    assert req.status_code == 200

    # Make sure entry changed
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {
        "id": 1,  # Still 1
        "competition": competition_participation.competition_id,
        "participant_name": "Pertti Perusjuntti",  # changed name
    }


@pytest.mark.django_db
def test_auth_competition_participation_instance_put(auth_client, competition_participation):
    instance_url = f"/api/v1/user_participations/{competition_participation.id}/"
    req = auth_client.put(
        instance_url,
        data={
            "competition": competition_participation.competition.id,
            "participant_name": "Pertti Partisipantti",
        },
    )
    assert req.status_code == 200

    # Make sure entry changed
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {
        "id": 1,  # Still 1
        "competition": competition_participation.competition_id,
        "participant_name": "Pertti Partisipantti",  # changed name
    }


@pytest.mark.django_db
def test_auth_competition_participation_instance_delete(auth_client, competition_participation):
    instance_url = f"/api/v1/user_participations/{competition_participation.id}/"
    assert auth_client.delete(instance_url).status_code == 204
    assert auth_client.get(instance_url).status_code == 404


@pytest.mark.django_db
def test_auth_competition_participation_instance_options(auth_client, competition_participation):
    instance_url = f"/api/v1/user_participations/{competition_participation.id}/"
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
def test_auth_compos(auth_client):
    url = "/api/v1/compos/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_compo_entries(auth_client):
    url = "/api/v1/compo_entries/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_user_entries_post(auth_client, open_compo, entry_zip, source_zip, image_png):
    url = "/api/v1/user_entries/"
    req = auth_client.post(
        url,
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
def test_auth_user_entries_post_uppercase_ext(auth_client, open_compo, entry_zip, source_zip, image_png):
    url = "/api/v1/user_entries/"
    entry_zip.name = "entry_file.ZIP"  # UPPERCASE EXTS
    source_zip.name = "source_file.ZIP"
    image_png.name = "image.PNG"
    req = auth_client.post(
        url,
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
def test_auth_user_entries_get(auth_client, editable_compo_entry):
    url = "/api/v1/user_entries/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert len(req.data) == 1
    data = req.data[0]
    assert data["id"] == editable_compo_entry.id
    assert data["compo"] == editable_compo_entry.compo_id
    assert data["name"] == editable_compo_entry.name
    assert data["description"] == editable_compo_entry.description
    assert data["creator"] == editable_compo_entry.creator
    assert data["platform"] == editable_compo_entry.platform
    assert data["entryfile_url"] is not None
    assert data["sourcefile_url"] is not None
    assert data["imagefile_original_url"] is not None
    assert data["imagefile_thumbnail_url"] is not None
    assert data["imagefile_medium_url"] is not None
    assert data["disqualified"] == editable_compo_entry.disqualified
    assert data["disqualified_reason"] == editable_compo_entry.disqualified_reason


@pytest.mark.django_db
def test_auth_user_entries_options(auth_client):
    url = "/api/v1/user_entries/"
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_user_entries_instance_patch(auth_client, editable_compo_entry):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"
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
    assert data["entryfile_url"] is not None
    assert data["sourcefile_url"] is not None
    assert data["imagefile_original_url"] is None
    assert data["imagefile_thumbnail_url"] is None
    assert data["imagefile_medium_url"] is None
    assert data["disqualified"] == editable_compo_entry.disqualified
    assert data["disqualified_reason"] == editable_compo_entry.disqualified_reason


@pytest.mark.django_db
def test_auth_user_entries_instance_put(
    auth_client, editable_compo_entry, entry_zip2, source_zip2, image_png2
):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"

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
    assert data["entryfile_url"] is not None
    assert data["sourcefile_url"] is not None
    assert data["imagefile_original_url"] is not None
    assert data["imagefile_thumbnail_url"] is not None
    assert data["imagefile_medium_url"] is not None
    assert data["disqualified"] == editable_compo_entry.disqualified
    assert data["disqualified_reason"] == editable_compo_entry.disqualified_reason


@pytest.mark.django_db
def test_auth_user_entries_instance_delete(auth_client, editable_compo_entry):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"
    assert auth_client.delete(instance_url).status_code == 204
    assert auth_client.get(instance_url).status_code == 404


@pytest.mark.django_db
def test_auth_user_entries_instance_options(auth_client, editable_compo_entry):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
def test_auth_programme_events(auth_client):
    url = "/api/v1/programme_events/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_store_items(auth_client):
    url = "/api/v1/store_items/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 403  # Unauthorized by permission class
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_store_transaction(auth_client):
    url = "/api/v1/store_transaction/"
    assert auth_client.get(url).status_code == 405
    assert auth_client.post(url).status_code == 400
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_current_user(auth_client, base_user):
    url = "/api/v1/current_user/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == {
        "id": base_user.id,
        "first_name": base_user.first_name,
        "last_name": base_user.last_name,
        "email": base_user.email,
    }
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_user_vote_code_post(auth_client, event, transaction_item_a):
    url = "/api/v1/user_vote_codes/"
    req = auth_client.post(url, data={"event": event.id, "ticket_key": transaction_item_a.key})
    assert req.status_code == 201


@pytest.mark.django_db
def test_auth_user_vote_code_post_duplicate(auth_client, ticket_vote_code):
    url = "/api/v1/user_vote_codes/"

    # Duplicate, should fail
    req = auth_client.post(
        url, data={"event": ticket_vote_code.event.id, "ticket_key": ticket_vote_code.ticket.key}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Äänestyskoodi on jo hankittu"]}


@pytest.mark.django_db
def test_auth_user_vote_code_get(auth_client, ticket_vote_code):
    url = "/api/v1/user_vote_codes/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": ticket_vote_code.id,
            "event": ticket_vote_code.event_id,
            "time": ticket_vote_code.time,
            "ticket_key": ticket_vote_code.ticket.key,
        }
    ]


@pytest.mark.django_db
def test_auth_user_vote_code_instance(auth_client, ticket_vote_code):
    # Test instance stuff. DELETE, PUT, PATCH = 405 (methods not implemented)
    instance_url = f"/api/v1/user_vote_codes/{ticket_vote_code.id}/"
    assert auth_client.put(instance_url, data={}).status_code == 405
    assert auth_client.delete(instance_url).status_code == 405
    assert auth_client.patch(instance_url, data={}).status_code == 405
    assert auth_client.get(instance_url).status_code == 200
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
def test_auth_user_vote_code_request_post(auth_client, event):
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.post(
        url,
        data={
            "event": event.id,
            "text": "Test request",
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_auth_user_vote_code_request_post_duplicate(auth_client, vote_code_request):
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.post(
        url,
        data={
            "event": vote_code_request.event_id,
            "text": "Test request",
        },
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Äänestyskoodipyyntö on jo olemassa"]}


@pytest.mark.django_db
def test_auth_user_vote_code_request_get(auth_client, vote_code_request):
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {"id": 1, "event": vote_code_request.event_id, "text": "gief vote code plsthx", "status": 0}
    ]


@pytest.mark.django_db
def test_auth_user_vote_code_request_options(auth_client, vote_code_request):
    url = "/api/v1/user_vote_code_requests/"
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_patch(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "id": 2,  # Should not change
            "text": "Test request 2",  # Should change
        },
    )
    assert req.status_code == 200

    # Make sure entry changed
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {"id": 1, "event": vote_code_request.event_id, "text": "Test request 2", "status": 0}


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_put(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    req = auth_client.put(
        instance_url,
        data={
            "event": vote_code_request.event_id,
            "text": "Test request",
        },
    )
    assert req.status_code == 200

    # Make sure entry changed
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {"id": 1, "event": vote_code_request.event_id, "text": "Test request", "status": 0}


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_delete(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    assert auth_client.delete(instance_url).status_code == 405  # No delete for this


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_options(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
def test_auth_user_vote_post_fail_not_started(auth_client, editable_compo_entry):
    """This should fail due to compo voting not started"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": editable_compo_entry.compo_id, "entries": [editable_compo_entry.id]}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Kompon äänestysaika ei ole voimassa"]}


@pytest.mark.django_db
def test_auth_user_vote_post_fail_missing_rights(auth_client, votable_compo_entry):
    """this should fail due to missing vote rights"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": votable_compo_entry.compo_id, "entries": [votable_compo_entry.id]}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Äänestysoikeus puuttuu"]}


@pytest.mark.django_db
def test_auth_user_vote_post_ok(auth_client, votable_compo_entry, ticket_vote_code):
    """this should succeed, as voting is open and we have voting rights"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": votable_compo_entry.compo_id, "entries": [votable_compo_entry.id]}
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_auth_user_vote_post_duplicate_ok(auth_client, votable_compo_entry, ticket_vote_code, entry_vote):
    """duplicate attempt should also succeed"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": votable_compo_entry.compo_id, "entries": [votable_compo_entry.id]}
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_auth_user_vote_get(auth_client, entry_vote):
    url = "/api/v1/user_votes/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [{"compo": entry_vote.entry.compo_id, "entries": [entry_vote.entry.id]}]


@pytest.mark.django_db
def test_auth_user_vote_instance(auth_client, entry_vote_group):
    """Test instance stuff. DELETE, PUT, PATCH = 405 (methods not implemented)"""
    instance_url = f"/api/v1/user_votes/{entry_vote_group.id}/"
    assert auth_client.put(instance_url, data={}).status_code == 405
    assert auth_client.delete(instance_url).status_code == 405
    assert auth_client.patch(instance_url, data={}).status_code == 405
    assert auth_client.get(instance_url).status_code == 200
    assert auth_client.options(instance_url).status_code == 200

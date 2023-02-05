import pytest


@pytest.mark.django_db
def test_events(api_client):
    url = "/api/v1/events/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_songs(api_client):
    url = "/api/v1/songs/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_competitions(api_client):
    url = "/api/v1/competitions/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_competition_participations(api_client):
    url = "/api/v1/competition_participations/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_user_participations(api_client):
    url = "/api/v1/user_participations/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_compos(api_client):
    url = "/api/v1/compos/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_compo_entries(api_client):
    url = "/api/v1/compo_entries/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_user_entries(api_client):
    url = "/api/v1/user_entries/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_programme_events(api_client):
    url = "/api/v1/programme_events/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_sponsors(api_client):
    url = "/api/v1/sponsors/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_messages(api_client):
    url = "/api/v1/messages/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_irc_message(api_client):
    url = "/api/v1/irc_messages/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 405
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_store_items(api_client):
    url = "/api/v1/store_items/"
    assert api_client.get(url).status_code == 200
    assert api_client.post(url).status_code == 403  # Unauthorized by permission class
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_store_transaction(api_client):
    url = "/api/v1/store_transaction/"
    assert api_client.get(url).status_code == 405
    assert api_client.post(url).status_code == 400  # No data = bad req. Tested properly in store tests.
    assert api_client.options(url).status_code == 200


@pytest.mark.django_db
def test_current_user(api_client):
    url = "/api/v1/current_user/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_user_vote_codes(api_client):
    url = "/api/v1/user_vote_codes/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_user_vote_code_requests(api_client):
    url = "/api/v1/user_vote_code_requests/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401


@pytest.mark.django_db
def test_user_votes(api_client):
    url = "/api/v1/user_votes/"
    assert api_client.get(url).status_code == 401
    assert api_client.post(url).status_code == 401
    assert api_client.options(url).status_code == 401

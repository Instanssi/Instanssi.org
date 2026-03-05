import pytest
from freezegun import freeze_time

from Instanssi.kompomaatti.models import LiveVotingState
from tests.conftest import FROZEN_TIME


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_is_voting_open_with_state_open(live_voting_compo, live_voting_state):
    """When state.voting_open=True, voting is open."""
    live_voting_state.voting_open = True
    live_voting_state.save()

    live_voting_compo.refresh_from_db()
    assert live_voting_compo.is_voting_open() is True


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_is_voting_open_with_state_closed(live_voting_compo, live_voting_state):
    """When state.voting_open=False, voting is closed."""
    live_voting_state.voting_open = False
    live_voting_state.save()

    live_voting_compo.refresh_from_db()
    assert live_voting_compo.is_voting_open() is False


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_is_voting_open_no_state(live_voting_compo):
    """When no LiveVotingState exists, voting is closed."""
    assert live_voting_compo.is_voting_open() is False

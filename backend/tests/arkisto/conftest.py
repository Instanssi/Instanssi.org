from datetime import datetime
from datetime import timezone as dt_tz

from django.core.files.uploadedfile import SimpleUploadedFile
from pytest import fixture

from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
)


@fixture
def archived_compo(archived_event) -> Compo:
    """Active compo in archived event with voting results shown."""
    return Compo.objects.create(
        event=archived_event,
        name="Archived Compo",
        description="A compo in an archived event",
        show_voting_results=True,
        adding_end=datetime(2024, 1, 10, 12, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2024, 1, 11, 12, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2024, 1, 12, 12, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2024, 1, 12, 13, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2024, 1, 13, 12, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def hidden_from_archive_compo(archived_event) -> Compo:
    """Compo in archived event that is hidden from archive."""
    return Compo.objects.create(
        event=archived_event,
        name="Hidden Compo",
        description="A compo hidden from the archive",
        hide_from_archive=True,
        adding_end=datetime(2024, 1, 10, 12, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2024, 1, 11, 12, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2024, 1, 12, 12, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2024, 1, 12, 13, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2024, 1, 13, 12, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def inactive_archived_compo(archived_event) -> Compo:
    """Inactive compo in archived event."""
    return Compo.objects.create(
        event=archived_event,
        name="Inactive Compo",
        description="An inactive compo in an archived event",
        active=False,
        adding_end=datetime(2024, 1, 10, 12, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2024, 1, 11, 12, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2024, 1, 12, 12, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2024, 1, 12, 13, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2024, 1, 13, 12, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def archived_entry(base_user, archived_compo, entry_zip, image_png) -> Entry:
    """Entry in an archived compo."""
    return Entry.objects.create(
        compo=archived_compo,
        user=base_user,
        name="Archived Entry",
        description="An entry in an archived compo",
        creator="Test Creator",
        entryfile=entry_zip,
        imagefile_original=image_png,
    )


@fixture
def hidden_compo_entry(base_user, hidden_from_archive_compo, entry_zip) -> Entry:
    """Entry in a hidden-from-archive compo."""
    return Entry.objects.create(
        compo=hidden_from_archive_compo,
        user=base_user,
        name="Hidden Compo Entry",
        description="An entry in a hidden compo",
        creator="Hidden Creator",
        entryfile=SimpleUploadedFile("hidden_entry.zip", b"PK\x05\x06" + b"\x00" * 18),
    )


@fixture
def archived_competition(archived_event) -> Competition:
    """Competition in an archived event."""
    return Competition.objects.create(
        event=archived_event,
        name="Archived Competition",
        description="A competition in an archived event",
        participation_end=datetime(2024, 1, 12, 12, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2024, 1, 12, 13, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2024, 1, 12, 14, 0, 0, tzinfo=dt_tz.utc),
        score_type="pts",
        show_results=True,
    )


@fixture
def archived_participation(base_user, archived_competition) -> CompetitionParticipation:
    """Participation in an archived competition."""
    return CompetitionParticipation.objects.create(
        competition=archived_competition,
        user=base_user,
        participant_name="Test Participant",
        score=42.0,
    )

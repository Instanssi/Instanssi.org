import base64
import secrets
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from datetime import timezone as dt_tz
from decimal import Decimal
from pathlib import Path
from shutil import rmtree
from typing import Any, Callable, Dict
from uuid import uuid4

from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from pytest import fixture
from rest_framework.test import APIClient

from Instanssi.admin_upload.models import UploadedFile
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
from Instanssi.ext_blog.models import BlogEntry
from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.enums import MediaCodec, MediaContainer
from Instanssi.kompomaatti.models import (
    AlternateEntryFile,
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    TicketVoteCode,
    Vote,
    VoteCodeRequest,
    VoteGroup,
)
from Instanssi.store.models import (
    Receipt,
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    TransactionItem,
)
from Instanssi.store.utils.receipt import ReceiptParams
from Instanssi.users.models import User

# All time-sensitive fixtures use datetimes relative to this frozen time.
# Tests that check time-dependent behavior should use @freeze_time(FROZEN_TIME).
FROZEN_TIME = "2025-01-15T12:00:00Z"


@fixture(scope="session")
def faker() -> Faker:
    return Faker("fi_FI")


@fixture(scope="session", autouse=True)
def set_media_root():
    """
    Use mkdtemp to generate us a temp path and feed it in as django MEDIA_ROOT.
    This way we can put our test uploads to their own special place and remove
    them after tests.
    """
    tmp_path = Path(tempfile.mkdtemp(prefix="pytest_"))
    try:
        with override_settings(MEDIA_ROOT=tmp_path):
            yield
    finally:
        rmtree(tmp_path)


@fixture
def test_image() -> bytes:
    return base64.decodebytes(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeA"
        b"AAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcE"
        b"hZcwAADsMAAA7DAcdvqGQAAAAMSURBVBhXY2BgYAAAAAQ"
        b"AAVzN/2kAAAAASUVORK5CYII="
    )


@fixture
def test_zip() -> bytes:
    """A zip file with a single, empty text file as content."""
    return base64.decodebytes(
        b"UEsDBAoAAAAAALRwhlUAAAAAAAAAAAAAAAAIAAAAdGVzd"
        b"C50eHRQSwECPwAKAAAAAAC0cIZVAAAAAAAAAAAAAAAA"
        b"CAAkAAAAAAAAACAAAAAAAAAAdGVzdC50eHQKACAAAAAAA"
        b"AEAGABs1dUNawnZAWzV1Q1rCdkBbNXVDWsJ2QFQSwUG"
        b"AAAAAAEAAQBaAAAAJgAAAAAA"
    )


@fixture
def entry_zip(test_zip) -> SimpleUploadedFile:
    return SimpleUploadedFile("test_entry_file.zip", test_zip, content_type="application/zip")


@fixture
def entry_zip2(test_zip) -> SimpleUploadedFile:
    return SimpleUploadedFile("another_test_entry_file.zip", test_zip, content_type="application/zip")


@fixture
def source_zip(test_zip) -> SimpleUploadedFile:
    return SimpleUploadedFile("test_source_file.zip", test_zip, content_type="application/zip")


@fixture
def source_zip2(test_zip) -> SimpleUploadedFile:
    return SimpleUploadedFile("another_test_source_file.zip", test_zip, content_type="application/zip")


@fixture
def image_png(test_image) -> SimpleUploadedFile:
    return SimpleUploadedFile("test_image_file.png", test_image, content_type="image/png")


@fixture
def image_png2(test_image) -> SimpleUploadedFile:
    return SimpleUploadedFile("another_test_image_file.png", test_image, content_type="image/png")


@fixture
def page_client() -> Client:
    """Use this to test normal (non-api) Django pages"""
    return Client()


@fixture
def login_as(page_client, password, create_user):
    @contextmanager
    def _inner(**kwargs):
        user = create_user(**kwargs)
        page_client.login(username=user.username, password=password)
        yield page_client
        page_client.logout()

    return _inner


@fixture
def password() -> str:
    return secrets.token_hex(16)


@fixture
def staff_page_client(page_client, staff_user, password) -> APIClient:
    page_client.login(username=staff_user.username, password=password)
    yield page_client
    page_client.logout()


@fixture
def super_page_client(page_client, super_user, password) -> APIClient:
    page_client.login(username=super_user.username, password=password)
    yield page_client
    page_client.logout()


@fixture
def create_user(faker, password):
    def _inner(**kwargs) -> User:
        permissions = kwargs.pop("permissions", [])
        obj: User = User.objects.create_user(
            username=faker.user_name(),
            email=faker.email(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password=password,
            **kwargs,
        )
        if permissions:
            for permission in permissions:
                app, name = permission.split(".")
                obj.user_permissions.add(Permission.objects.get(content_type__app_label=app, codename=name))

        return obj

    return _inner


@fixture
def base_user(create_user) -> User:
    return create_user()


@fixture
def normal_user(create_user) -> User:
    return create_user(is_staff=False)


@fixture
def staff_user(create_user) -> User:
    # Grant all kompomaatti and ext_programme permissions to staff users for testing
    permissions = [
        "kompomaatti.view_event",
        "kompomaatti.add_event",
        "kompomaatti.change_event",
        "kompomaatti.delete_event",
        "kompomaatti.view_compo",
        "kompomaatti.add_compo",
        "kompomaatti.change_compo",
        "kompomaatti.delete_compo",
        "kompomaatti.view_entry",
        "kompomaatti.add_entry",
        "kompomaatti.change_entry",
        "kompomaatti.delete_entry",
        "kompomaatti.view_vote",
        "kompomaatti.delete_vote",
        "kompomaatti.view_competition",
        "kompomaatti.add_competition",
        "kompomaatti.change_competition",
        "kompomaatti.delete_competition",
        "kompomaatti.view_competitionparticipation",
        "kompomaatti.add_competitionparticipation",
        "kompomaatti.change_competitionparticipation",
        "kompomaatti.delete_competitionparticipation",
        "kompomaatti.view_votecoderequest",
        "kompomaatti.add_votecoderequest",
        "kompomaatti.change_votecoderequest",
        "kompomaatti.delete_votecoderequest",
        "kompomaatti.view_ticketvotecode",
        "kompomaatti.add_ticketvotecode",
        "kompomaatti.change_ticketvotecode",
        "kompomaatti.delete_ticketvotecode",
        "ext_programme.view_programmeevent",
        "ext_programme.add_programmeevent",
        "ext_programme.change_programmeevent",
        "ext_programme.delete_programmeevent",
        "arkisto.view_othervideocategory",
        "arkisto.add_othervideocategory",
        "arkisto.change_othervideocategory",
        "arkisto.delete_othervideocategory",
        "arkisto.view_othervideo",
        "arkisto.add_othervideo",
        "arkisto.change_othervideo",
        "arkisto.delete_othervideo",
        "admin_upload.view_uploadedfile",
        "admin_upload.add_uploadedfile",
        "admin_upload.change_uploadedfile",
        "admin_upload.delete_uploadedfile",
        "knox.view_authtoken",
        "knox.add_authtoken",
        "knox.delete_authtoken",
    ]
    return create_user(is_staff=True, permissions=permissions)


@fixture
def super_user(create_user) -> User:
    return create_user(is_staff=True, is_superuser=True)


@fixture
def event() -> Event:
    return Event.objects.create(
        name="Instanssi 2025",
        tag="2025",
        date=date(2025, 1, 15),
        archived=False,
        mainurl="http://localhost:8000/2025/",
    )


@fixture
def other_event() -> Event:
    """A second event for testing cross-event validation."""
    return Event.objects.create(
        name="Other Event 2025",
        tag="other2025",
        date=date(2025, 2, 15),
        archived=False,
        mainurl="http://localhost:8000/other2025/",
    )


@fixture
def blog_entry(event, base_user) -> BlogEntry:
    """Non-public blog entry (only visible to staff)"""
    return BlogEntry.objects.create(
        event=event,
        user=base_user,
        title="Test post",
        text="This is a non-public test blog entry.",
        date=datetime(2024, 1, 15, 12, 0, 0, tzinfo=dt_tz.utc),
        public=False,
    )


@fixture
def public_blog_entry(event, base_user) -> BlogEntry:
    """Public blog entry (visible to everyone)"""
    return BlogEntry.objects.create(
        event=event,
        user=base_user,
        title="Public test post",
        text="This is a public test blog entry.",
        date=datetime(2024, 1, 15, 12, 0, 0, tzinfo=dt_tz.utc),
        public=True,
    )


@fixture
def program_event(event) -> ProgrammeEvent:
    """Active program event for testing."""
    return ProgrammeEvent.objects.create(
        event=event,
        start=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        title="Test Programme Event",
        description="A test programme event",
        presenters="Test Presenter",
        place="Main Stage",
        active=True,
    )


@fixture
def inactive_program_event(event) -> ProgrammeEvent:
    """Inactive program event for testing visibility."""
    return ProgrammeEvent.objects.create(
        event=event,
        start=datetime(2025, 1, 15, 15, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 16, 0, 0, tzinfo=dt_tz.utc),
        title="Inactive Programme Event",
        description="An inactive programme event",
        presenters="Inactive Presenter",
        place="Side Stage",
        active=False,
    )


@fixture
def archived_event() -> Event:
    """Archived event for testing archive visibility."""
    return Event.objects.create(
        name="Instanssi Archive 2024",
        tag="archive-2024",
        date=date(2024, 1, 15),
        archived=True,
        mainurl="http://localhost:8000/archive-2024/",
    )


@fixture
def non_archived_event() -> Event:
    """Non-archived event for testing archive visibility."""
    return Event.objects.create(
        name="Instanssi Current 2025",
        tag="current-2025",
        date=date(2025, 1, 15),
        archived=False,
        mainurl="http://localhost:8000/current-2025/",
    )


@fixture
def video_category(archived_event) -> OtherVideoCategory:
    """Video category for an archived event."""
    return OtherVideoCategory.objects.create(
        event=archived_event,
        name="Test Videos",
    )


@fixture
def video_category_non_archived(non_archived_event) -> OtherVideoCategory:
    """Video category for a non-archived event (not publicly visible)."""
    return OtherVideoCategory.objects.create(
        event=non_archived_event,
        name="Current Videos",
    )


@fixture
def other_video(video_category) -> OtherVideo:
    """Video for an archived event."""
    return OtherVideo.objects.create(
        category=video_category,
        name="Test Video",
        description="A test video description",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )


@fixture
def other_video_non_archived(video_category_non_archived) -> OtherVideo:
    """Video for a non-archived event (not publicly visible)."""
    return OtherVideo.objects.create(
        category=video_category_non_archived,
        name="Current Video",
        description="A current video description",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )


# Compo fixtures - all times relative to FROZEN_TIME (2025-01-15T12:00:00Z)


@fixture
def upcoming_compo(event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Upcoming Compo",
        description="This compo cannot be participated in yet!",
        adding_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 18, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 18, 30, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def open_compo(event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Open Compo",
        description="Test Compo should be open for participations!",
        adding_end=datetime(2025, 1, 15, 12, 30, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 15, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def votable_compo(event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Votable Compo",
        description="Test Compo should be votable!",
        adding_end=datetime(2025, 1, 15, 6, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 11, 30, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def second_votable_compo(faker, event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Second Votable Compo",
        description="Another votable test compo!",
        adding_end=timezone.now() + timedelta(hours=-6),
        editing_end=timezone.now() + timedelta(hours=-2),
        compo_start=timezone.now() + timedelta(hours=-1),
        voting_start=timezone.now() + timedelta(minutes=-30),
        voting_end=timezone.now() + timedelta(hours=8),
    )


@fixture
def closed_compo(event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Closed Compo",
        description="Test Compo should be closed!",
        adding_end=datetime(2025, 1, 15, 6, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 11, 30, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 11, 55, 0, tzinfo=dt_tz.utc),
    )


@fixture
def inactive_compo(event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Inactive Compo",
        description="Test Compo is not active!",
        active=False,
        adding_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 15, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 16, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def editable_compo_entry(base_user, open_compo, entry_zip, source_zip, image_png) -> Entry:
    return Entry.objects.create(
        compo=open_compo,
        user=base_user,
        name="Test Entry",
        description="An editable test entry",
        creator="Test Creator",
        platform="Commodore 64",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )


@fixture
def closed_compo_entry(base_user, closed_compo, entry_zip, source_zip, image_png) -> Entry:
    return Entry.objects.create(
        compo=closed_compo,
        user=base_user,
        name="Closed Entry",
        description="A closed test entry",
        creator="Closed Creator",
        platform="Commodore 64",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
        archive_score=5,
        archive_rank=1,
    )


@fixture
def votable_compo_entry(base_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    return Entry.objects.create(
        compo=votable_compo,
        user=base_user,
        name="Test Entry",
        description="A votable test entry",
        creator="Test Creator",
        platform="Commodore 64",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )


@fixture
def second_votable_entry(normal_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    """A second entry in the votable compo."""
    return Entry.objects.create(
        compo=votable_compo,
        user=normal_user,
        name="Second Entry",
        description="A second votable entry",
        creator="Second Creator",
        platform="Amiga",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )


@fixture
def third_votable_entry(normal_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    """A third entry in the votable compo."""
    return Entry.objects.create(
        compo=votable_compo,
        user=normal_user,
        name="Third Entry",
        description="A third votable entry",
        creator="Third Creator",
        platform="PC",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )


@fixture
def votable_alternate_entry_file(votable_compo_entry, test_zip) -> AlternateEntryFile:
    """Alternate audio file for a votable entry (simulates transcoded audio)."""
    audio_file = SimpleUploadedFile("alternate.webm", test_zip, content_type="audio/webm")
    return AlternateEntryFile.objects.create(
        entry=votable_compo_entry,
        codec=MediaCodec.OPUS,
        container=MediaContainer.WEBM,
        file=audio_file,
    )


@fixture
def editable_alternate_entry_file(editable_compo_entry, test_zip) -> AlternateEntryFile:
    """Alternate audio file for an editable entry (for user endpoint tests)."""
    audio_file = SimpleUploadedFile("user_alternate.webm", test_zip, content_type="audio/webm")
    return AlternateEntryFile.objects.create(
        entry=editable_compo_entry,
        codec=MediaCodec.OPUS,
        container=MediaContainer.WEBM,
        file=audio_file,
    )


# Competition fixtures - all times relative to FROZEN_TIME (2025-01-15T12:00:00Z)


@fixture
def competition(event) -> Competition:
    """Competition that hasn't started yet"""
    return Competition.objects.create(
        event=event,
        name="Test competition",
        description="<p>Test competition is the <strong>awesomest</strong> ever!</p>",
        participation_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 15, 13, 30, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
    )


@fixture
def started_competition(event) -> Competition:
    """Competition that has already started"""
    return Competition.objects.create(
        event=event,
        name="Started Competition",
        description="<p>Test competition that has <em>started</em></p>",
        participation_end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 14, 5, 30, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
    )


@fixture
def inactive_competition(event) -> Competition:
    """Inactive competition (not shown to public)"""
    return Competition.objects.create(
        event=event,
        name="Inactive Competition",
        description="<p>Test competition that is <strong>inactive</strong></p>",
        active=False,
        participation_end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 14, 5, 30, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
    )


@fixture
def results_competition(event) -> Competition:
    """Competition with show_results=True."""
    return Competition.objects.create(
        event=event,
        name="Results Competition",
        description="<p>Competition with visible results</p>",
        participation_end=datetime(2025, 1, 14, 12, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 14, 13, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
        show_results=True,
    )


@fixture
def second_competition(event) -> Competition:
    """A second competition in the same event (for partitioning tests)."""
    return Competition.objects.create(
        event=event,
        name="Second Test Competition",
        description="<p>Another competition in the same event</p>",
        participation_end=timezone.now() + timedelta(hours=1),
        start=timezone.now() + timedelta(hours=2),
        end=timezone.now() + timedelta(hours=8),
        score_type="p",
    )


@fixture
def lower_is_better_competition(event) -> Competition:
    """Competition where lower scores are better (e.g., time trials)."""
    return Competition.objects.create(
        event=event,
        name="Time Trial",
        description="<p>Competition where lowest time wins</p>",
        participation_end=timezone.now() + timedelta(hours=1),
        start=timezone.now() + timedelta(hours=2),
        end=timezone.now() + timedelta(hours=8),
        score_type="sec",
        score_sort=1,  # Lower is better
    )


@fixture
def competition_participation(competition, base_user) -> CompetitionParticipation:
    return CompetitionParticipation.objects.create(
        competition=competition, user=base_user, participant_name="Test Participant", score=100.0
    )


@fixture
def started_competition_participation(started_competition, base_user) -> CompetitionParticipation:
    return CompetitionParticipation.objects.create(
        competition=started_competition, user=base_user, participant_name="Started Participant", score=150.0
    )


@fixture
def other_user_competition_participation(started_competition, normal_user) -> CompetitionParticipation:
    """Participation belonging to another user (normal_user)."""
    return CompetitionParticipation.objects.create(
        competition=started_competition, user=normal_user, participant_name="Other Participant", score=75.0
    )


@fixture
def normal_user_competition_participation(faker, competition, normal_user) -> CompetitionParticipation:
    """Participation for normal_user in competition."""
    return CompetitionParticipation.objects.create(
        competition=competition, user=normal_user, participant_name=faker.name(), score=0
    )


@fixture
def staff_competition_participation(faker, competition, staff_user) -> CompetitionParticipation:
    """Participation for staff_user in competition."""
    return CompetitionParticipation.objects.create(
        competition=competition, user=staff_user, participant_name=faker.name(), score=0
    )


@fixture
def second_competition_participation(faker, second_competition, normal_user) -> CompetitionParticipation:
    """Participation in the second competition."""
    return CompetitionParticipation.objects.create(
        competition=second_competition, user=normal_user, participant_name=faker.name(), score=0
    )


@fixture
def lower_competition_participation(
    faker, lower_is_better_competition, base_user
) -> CompetitionParticipation:
    """Participation in the lower-is-better competition for base_user."""
    return CompetitionParticipation.objects.create(
        competition=lower_is_better_competition, user=base_user, participant_name=faker.name(), score=0
    )


@fixture
def lower_normal_competition_participation(
    faker, lower_is_better_competition, normal_user
) -> CompetitionParticipation:
    """Participation in the lower-is-better competition for normal_user."""
    return CompetitionParticipation.objects.create(
        competition=lower_is_better_competition, user=normal_user, participant_name=faker.name(), score=0
    )


@fixture
def lower_staff_competition_participation(
    faker, lower_is_better_competition, staff_user
) -> CompetitionParticipation:
    """Participation in the lower-is-better competition for staff_user."""
    return CompetitionParticipation.objects.create(
        competition=lower_is_better_competition, user=staff_user, participant_name=faker.name(), score=0
    )


@fixture
def inactive_competition_participation(inactive_competition, base_user) -> CompetitionParticipation:
    """Participation in an inactive competition."""
    return CompetitionParticipation.objects.create(
        competition=inactive_competition, user=base_user, participant_name="Inactive Participant", score=50.0
    )


@fixture
def results_competition_participation(results_competition, base_user) -> CompetitionParticipation:
    """Participation in a competition with results shown."""
    return CompetitionParticipation.objects.create(
        competition=results_competition, user=base_user, participant_name="Results Participant", score=150.0
    )


@fixture
def store_transaction(event) -> StoreTransaction:
    return StoreTransaction.objects.create(
        token="aabbccdd11223344",
        time_created=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        time_paid=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        key="deadbeef12345678deadbeef12345678",
        firstname="Testi",
        lastname="Asiakas",
        email="testi.asiakas@instanssi.org",
        street="Kauppakatu 1",
        postalcode="00100",
        city="Helsinki",
    )


@fixture
def transaction_item_a(store_item, store_transaction) -> TransactionItem:
    return TransactionItem.objects.create(
        key="aaaa1111bbbb2222cccc3333dddd4444",
        item=store_item,
        transaction=store_transaction,
        time_delivered=datetime(2025, 1, 15, 10, 30, 0, tzinfo=dt_tz.utc),
        purchase_price=Decimal("2.50"),
        original_price=Decimal("2.50"),
    )


@fixture
def transaction_item_b(store_item, store_transaction) -> TransactionItem:
    return TransactionItem.objects.create(
        key="eeee4444ffff5555aaaa6666bbbb7777",
        item=store_item,
        transaction=store_transaction,
        time_delivered=datetime(2025, 1, 15, 10, 30, 0, tzinfo=dt_tz.utc),
        purchase_price=Decimal("1.00"),
        original_price=Decimal("1.00"),
    )


@fixture
def transaction_item_generator(store_transaction):
    def _generator(store_item, price=Decimal("1.00"), variant=None):
        return TransactionItem.objects.create(
            key=uuid4().hex,
            item=store_item,
            transaction=store_transaction,
            time_delivered=None,
            purchase_price=price,
            original_price=price,
            variant=variant,
        )

    return _generator


@fixture
def ticket_vote_code(event, base_user, transaction_item_a) -> TicketVoteCode:
    return TicketVoteCode.objects.create(
        event=event,
        ticket=transaction_item_a,
        associated_to=base_user,
    )


@fixture
def claimable_ticket(store_item, store_transaction) -> TransactionItem:
    """A paid ticket that can be claimed for voting rights (not yet used by any vote code)."""
    return TransactionItem.objects.create(
        key="cccc8888dddd9999eeee0000ffff1111",
        item=store_item,
        transaction=store_transaction,
        purchase_price=store_item.price,
        original_price=store_item.price,
    )


@fixture
def unpaid_transaction() -> StoreTransaction:
    """An unpaid transaction."""
    return StoreTransaction.objects.create(
        token="eeff0011aabb2233",
        time_created=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        time_paid=None,  # Not paid
        key="cafebabe12345678cafebabe12345678",
        firstname="Testi",
        lastname="Maksamaton",
        email="testi.maksamaton@instanssi.org",
        street="Maksukatu 1",
        postalcode="00100",
        city="Helsinki",
    )


@fixture
def unpaid_ticket(store_item, unpaid_transaction) -> TransactionItem:
    """A ticket from an unpaid transaction."""
    return TransactionItem.objects.create(
        key="2222333344445555666677778888aaaa",
        item=store_item,
        transaction=unpaid_transaction,
        purchase_price=store_item.price,
        original_price=store_item.price,
    )


@fixture
def non_ticket_transaction_item(variant_item, store_transaction) -> TransactionItem:
    """A transaction item for a non-ticket store item."""
    return TransactionItem.objects.create(
        key="bbbb1111cccc2222dddd3333eeee4444",
        item=variant_item,
        transaction=store_transaction,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def other_user_ticket_vote_code(event, normal_user, transaction_item_b) -> TicketVoteCode:
    """A ticket vote code belonging to another user (normal_user)."""
    return TicketVoteCode.objects.create(
        event=event,
        ticket=transaction_item_b,
        associated_to=normal_user,
    )


@fixture
def vote_code_request(event, base_user) -> VoteCodeRequest:
    return VoteCodeRequest.objects.create(
        event=event,
        user=base_user,
        text="gief vote code plsthx",
        status=0,
    )


@fixture
def approved_vote_code_request(event, base_user) -> VoteCodeRequest:
    """Approved vote code request for base_user."""
    return VoteCodeRequest.objects.create(
        event=event,
        user=base_user,
        text="Please give me voting rights",
        status=1,  # Approved
    )


@fixture
def rejected_vote_code_request(event, base_user) -> VoteCodeRequest:
    """Rejected vote code request for base_user."""
    return VoteCodeRequest.objects.create(
        event=event,
        user=base_user,
        text="Please give me voting rights",
        status=2,  # Rejected
    )


@fixture
def other_user_vote_code_request(event, normal_user) -> VoteCodeRequest:
    """Vote code request belonging to another user (normal_user)."""
    return VoteCodeRequest.objects.create(
        event=event,
        user=normal_user,
        text="Other user's request",
        status=0,
    )


@fixture
def entry_vote_group(base_user, votable_compo) -> VoteGroup:
    return VoteGroup.objects.create(
        user=base_user,
        compo=votable_compo,
    )


@fixture
def other_user_vote_group(normal_user, votable_compo) -> VoteGroup:
    """Vote group belonging to another user (normal_user)."""
    return VoteGroup.objects.create(
        user=normal_user,
        compo=votable_compo,
    )


@fixture
def entry_vote(base_user, votable_compo_entry, votable_compo, entry_vote_group) -> Vote:
    return Vote.objects.create(
        user=base_user,
        compo=votable_compo,
        entry=votable_compo_entry,
        rank=0,
        group=entry_vote_group,
    )


@fixture
def base_store_item(event, image_png) -> Callable[[], StoreItem]:
    def _inner() -> StoreItem:
        return StoreItem(
            name="Test item 1",
            event=event,
            description="A test store item",
            price=Decimal("20.00"),
            max=50,
            available=True,
            max_per_order=5,
            sort_index=0,
            discount_amount=-1,
            discount_percentage=0,
            is_ticket=True,
            secret_key="",
            imagefile_original=image_png,
        )

    return _inner


@fixture
def store_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.save()
    return store_item


@fixture
def hidden_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.name = "Secret item"
    store_item.is_secret = True
    store_item.secret_key = "kissa"
    store_item.save(force_insert=True)
    return store_item


@fixture
def variant_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.is_ticket = False
    store_item.save()
    return store_item


@fixture
def discount_item(base_store_item) -> StoreItem:
    store_item = base_store_item()
    store_item.discount_amount = 5
    store_item.discount_percentage = 50
    store_item.save()
    return store_item


@fixture
def store_item_variant(variant_item) -> StoreItemVariant:
    return StoreItemVariant.objects.create(item=variant_item, name="XXL")


@fixture
def store_item_variant2(variant_item) -> StoreItemVariant:
    return StoreItemVariant.objects.create(item=variant_item, name="S")


@fixture
def new_transaction(event) -> StoreTransaction:
    return StoreTransaction.objects.create(
        time_created=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        key="a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8",
        firstname="Testi",
        lastname="Ostaja",
        email="testi.ostaja@instanssi.org",
        street="Ostoskatu 1",
        postalcode="00100",
        city="Helsinki",
        information="Test transaction",
    )


@fixture
def new_transaction_item(new_transaction, variant_item, store_item_variant) -> TransactionItem:
    return TransactionItem.objects.create(
        key="1111aaaa2222bbbb3333cccc4444dddd",
        transaction=new_transaction,
        item=variant_item,
        variant=store_item_variant,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def new_transaction_item_copy(new_transaction, variant_item, store_item_variant) -> TransactionItem:
    return TransactionItem.objects.create(
        key="5555eeee6666ffff7777aaaa8888bbbb",
        transaction=new_transaction,
        item=variant_item,
        variant=store_item_variant,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def new_transaction_item2(new_transaction, variant_item, store_item_variant2) -> TransactionItem:
    return TransactionItem.objects.create(
        key="9999cccc0000dddd1111eeee2222ffff",
        transaction=new_transaction,
        item=variant_item,
        variant=store_item_variant2,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def new_transaction_item3(new_transaction, store_item) -> TransactionItem:
    return TransactionItem.objects.create(
        key="3333aaaa4444bbbb5555cccc6666dddd",
        transaction=new_transaction,
        item=store_item,
        variant=None,
        purchase_price=store_item.price,
        original_price=store_item.price,
    )


@fixture
def new_transaction_item4(new_transaction, hidden_item) -> TransactionItem:
    return TransactionItem.objects.create(
        key="7777eeee8888ffff9999aaaa0000bbbb",
        transaction=new_transaction,
        item=hidden_item,
        variant=None,
        purchase_price=hidden_item.price,
        original_price=hidden_item.price,
    )


@fixture
def receipt_params() -> ReceiptParams:
    request = RequestFactory().get("/")
    p = ReceiptParams()
    p.order_number(20000)
    p.receipt_number(1000)
    p.receipt_date(datetime(2025, 1, 15, 12, 0, 0, tzinfo=dt_tz.utc))
    p.order_date(datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc))
    p.first_name("Testi")
    p.last_name("Testinen")
    p.email("testi@instanssi.org")
    p.mobile("+358401234567")
    p.telephone("091234567")
    p.company("Test Oy")
    p.street("Testikatu 1")
    p.city("Helsinki")
    p.postal_code("00100")
    p.country("FI")
    p.transaction_url(request.build_absolute_uri(reverse("store:ta_view", args=("1234abcd",))))
    for k in range(3):
        p.add_item(
            item_id=str(1000 + k),
            price=Decimal(k),
            name=f"Test product {k}",
            amount=k,
            tax="0%",
        )
    return p


@fixture
def json_receipt_params(receipt_params) -> dict:
    params = receipt_params.params
    output = {
        "order_number": params["order_number"],
        "receipt_number": params["receipt_number"],
        "receipt_date": params["receipt_date"].isoformat(),
        "order_date": params["order_date"].isoformat(),
        "first_name": params["first_name"],
        "last_name": params["last_name"],
        "mobile": params["mobile"],
        "email": params["email"],
        "telephone": params["telephone"],
        "company": params["company"],
        "street": params["street"],
        "city": params["city"],
        "postal_code": params["postal_code"],
        "country": params["country"],
        "items": [],
        "transaction_url": params["transaction_url"],
        "total": str(params["total"]),
    }
    for item in params["items"]:
        output["items"].append(
            {
                "id": item["id"],
                "name": item["name"],
                "price": str(item["price"]),
                "amount": item["amount"],
                "total": str(item["total"]),
                "tax": item["tax"],
            }
        )
    return output


@fixture
def receipt(receipt_params) -> Receipt:
    return Receipt.create(
        mail_to=receipt_params.params["email"],
        mail_from="Instanssi.org <noreply@instanssi.org>",
        subject="Test email",
        params=receipt_params,
    )


@fixture
def store_receipt(store_transaction, receipt_params) -> Receipt:
    """Create a receipt linked to a store transaction."""
    return Receipt.create(
        mail_to=receipt_params.params["email"],
        mail_from="test@instanssi.org",
        subject="Test Receipt",
        params=receipt_params,
        transaction=store_transaction,
    )


@fixture
def empty_receipt(store_transaction) -> Receipt:
    """Create a receipt without content (for testing edge cases)."""
    return Receipt.objects.create(
        transaction=store_transaction,
        subject="Empty Receipt",
        mail_to="test@example.com",
        mail_from="test@instanssi.org",
        content=None,
    )


@fixture
def transaction_base() -> Dict[str, Any]:
    """Common base for creating new transactions via create_store_transaction()"""
    return {
        "first_name": "Donald",
        "last_name": "Duck",
        "company": "Duck Co",
        "email": "donald.duck@duckburg.inv",
        "telephone": "991234567",
        "mobile": "+358991234567",
        "street": "1313 Webfoot Walk",
        "postal_code": "00000",
        "city": "Duckburg",
        "country": "US",
        "information": "Quack, damn you!",
        "items": [],
    }


# Event validation fixtures - for testing cross-event validation


@fixture
def other_event_video_category(other_event) -> OtherVideoCategory:
    """Video category belonging to a different event."""
    return OtherVideoCategory.objects.create(
        event=other_event,
        name="Other Event Category",
    )


@fixture
def other_competition(other_event) -> Competition:
    """Competition belonging to a different event."""
    return Competition.objects.create(
        event=other_event,
        name="Other Competition",
        description="<p>Competition from <em>another</em> event</p>",
        participation_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
        active=True,
    )


@fixture
def other_event_store_item(other_event) -> StoreItem:
    """Store item belonging to a different event."""
    return StoreItem.objects.create(
        event=other_event,
        name="Other Event Item",
        description="Item from another event",
        price=10,
        max=100,
        available=True,
    )


@fixture
def other_event_transaction(other_event) -> StoreTransaction:
    """Transaction with items from a different event."""
    store_item = StoreItem.objects.create(
        event=other_event,
        name="Other Event Transaction Item",
        description="Item from another event for transaction",
        price=10,
        max=100,
        available=True,
    )
    transaction = StoreTransaction.objects.create(
        time_created=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        time_paid=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        key="1111222233334444aaaabbbbccccdddd",
        firstname="Other",
        lastname="Buyer",
        email="other.buyer@instanssi.org",
        street="Other Street 1",
        postalcode="00200",
        city="Espoo",
    )
    TransactionItem.objects.create(
        item=store_item,
        transaction=transaction,
        key="5555666677778888eeeeffff00001111",
        purchase_price=10,
        original_price=10,
    )
    return transaction


@fixture
def other_event_transaction_item(other_event) -> TransactionItem:
    """Transaction item from a store item belonging to a different event."""
    store_item = StoreItem.objects.create(
        event=other_event,
        name="Other Event Ticket",
        description="Ticket from another event",
        price=10,
        max=100,
        available=True,
    )
    transaction = StoreTransaction.objects.create(
        time_created=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        time_paid=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        key="9999aaaabbbbccccddddeeee11112222",
        firstname="Ticket",
        lastname="Buyer",
        email="ticket.buyer@instanssi.org",
        street="Ticket Street 1",
        postalcode="00300",
        city="Vantaa",
    )
    return TransactionItem.objects.create(
        item=store_item,
        transaction=transaction,
        key="3333444455556666777788889999aaaa",
        purchase_price=10,
        original_price=10,
    )


@fixture
def uploaded_file(event, staff_user, test_zip) -> UploadedFile:
    """Uploaded file for testing."""
    file = SimpleUploadedFile("test_upload.zip", test_zip, content_type="application/zip")
    return UploadedFile.objects.create(
        event=event,
        user=staff_user,
        description="Test uploaded file",
        file=file,
    )


@fixture
def other_event_uploaded_file(other_event, staff_user, test_zip) -> UploadedFile:
    """Uploaded file belonging to a different event."""
    file = SimpleUploadedFile("other_upload.zip", test_zip, content_type="application/zip")
    return UploadedFile.objects.create(
        event=other_event,
        user=staff_user,
        description="Other event uploaded file",
        file=file,
    )


@fixture
def archive_user() -> User:
    """The archive user that owns archived entries."""
    return User.objects.create_user(
        username="arkisto",
        email="arkisto@instanssi.org",
        password=None,
        is_active=False,
    )


@fixture
def past_event() -> Event:
    """Event that has ended (date in the past, for archiver tests)."""
    return Event.objects.create(
        name="Instanssi Past 2024",
        tag="past-2024",
        date=date(2024, 12, 16),
        archived=False,
        mainurl="http://localhost:8000/past-2024/",
    )


@fixture
def past_compo(past_event) -> Compo:
    """Compo that has ended (all deadlines in the past)."""
    return Compo.objects.create(
        event=past_event,
        name="Past Compo",
        description="This compo has ended",
        adding_end=datetime(2024, 12, 26, 12, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2024, 12, 27, 12, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2024, 12, 28, 12, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2024, 12, 29, 12, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 5, 12, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def past_compo_entry(base_user, past_compo, entry_zip, image_png) -> Entry:
    """Entry in a past compo (no archive scores set yet)."""
    return Entry.objects.create(
        compo=past_compo,
        user=base_user,
        name="Past Entry",
        description="A past test entry",
        creator="Past Creator",
        platform="PC",
        entryfile=entry_zip,
        imagefile_original=image_png,
    )


@fixture
def past_competition(past_event) -> Competition:
    """Competition that has ended."""
    return Competition.objects.create(
        event=past_event,
        name="Past Competition",
        description="<p>This competition has <strong>ended</strong></p>",
        participation_end=datetime(2024, 12, 26, 12, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2024, 12, 27, 12, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 5, 12, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
    )


@fixture
def past_competition_participation(past_competition, base_user) -> CompetitionParticipation:
    """Participation in a past competition."""
    return CompetitionParticipation.objects.create(
        competition=past_competition,
        user=base_user,
        participant_name="Past Participant",
        score=100.0,
    )


@fixture
def past_vote_group(base_user, past_compo) -> VoteGroup:
    """Vote group for a past compo."""
    return VoteGroup.objects.create(
        user=base_user,
        compo=past_compo,
    )


@fixture
def past_vote(base_user, past_compo, past_compo_entry, past_vote_group) -> Vote:
    """Vote in a past compo."""
    return Vote.objects.create(
        user=base_user,
        compo=past_compo,
        entry=past_compo_entry,
        rank=1,
        group=past_vote_group,
    )


# Hidden event fixtures - for testing hidden event filtering


@fixture
def hidden_event() -> Event:
    """A hidden event that should not appear in public/user APIs."""
    return Event.objects.create(
        name="Hidden Event 2025",
        tag="hidden-2025",
        date=date(2025, 1, 15),
        archived=False,
        hidden=True,
        mainurl="http://localhost:8000/hidden-2025/",
    )


@fixture
def hidden_archived_event() -> Event:
    """A hidden archived event that should not appear even in archive APIs."""
    return Event.objects.create(
        name="Hidden Archived Event 2024",
        tag="hidarch-2024",
        date=date(2024, 1, 15),
        archived=True,
        hidden=True,
        mainurl="http://localhost:8000/hidden-archived-2024/",
    )


@fixture
def hidden_event_compo(hidden_event) -> Compo:
    """Compo belonging to a hidden event."""
    return Compo.objects.create(
        event=hidden_event,
        name="Hidden Compo",
        description="This compo is in a hidden event",
        active=True,
        adding_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 15, 0, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
    )


@fixture
def hidden_event_entry(base_user, hidden_event_compo, entry_zip, image_png) -> Entry:
    """Entry in a hidden event's compo."""
    return Entry.objects.create(
        compo=hidden_event_compo,
        user=base_user,
        name="Hidden Entry",
        description="A hidden test entry",
        creator="Hidden Creator",
        platform="PC",
        entryfile=entry_zip,
        imagefile_original=image_png,
    )


@fixture
def hidden_event_competition(hidden_event) -> Competition:
    """Competition belonging to a hidden event."""
    return Competition.objects.create(
        event=hidden_event,
        name="Hidden Competition",
        description="<p>This competition is in a <em>hidden</em> event</p>",
        active=True,
        participation_end=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
    )


@fixture
def hidden_event_participation(base_user, hidden_event_competition) -> CompetitionParticipation:
    """Participation in a hidden event's competition."""
    return CompetitionParticipation.objects.create(
        competition=hidden_event_competition,
        user=base_user,
        participant_name="Hidden Participant",
        score=100.0,
    )


@fixture
def hidden_event_program(hidden_event) -> ProgrammeEvent:
    """Program event belonging to a hidden event."""
    return ProgrammeEvent.objects.create(
        event=hidden_event,
        start=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc),
        title="Hidden Programme Event",
        description="A hidden programme event",
        presenters="Hidden Presenter",
        place="Main Stage",
        active=True,
    )


@fixture
def hidden_event_video_category(hidden_archived_event) -> OtherVideoCategory:
    """Video category belonging to a hidden archived event."""
    return OtherVideoCategory.objects.create(
        event=hidden_archived_event,
        name="Hidden Videos",
    )


@fixture
def hidden_event_blog_entry(hidden_event, base_user) -> BlogEntry:
    """Blog entry belonging to a hidden event."""
    return BlogEntry.objects.create(
        event=hidden_event,
        user=base_user,
        title="Hidden Blog Post",
        text="This blog entry is in a hidden event.",
        date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=dt_tz.utc),
        public=True,
    )


@fixture
def hidden_event_store_item(hidden_event) -> StoreItem:
    """Store item belonging to a hidden event."""
    return StoreItem.objects.create(
        event=hidden_event,
        name="Hidden Event Ticket",
        description="Ticket for a hidden event",
        price=Decimal("20.00"),
        max=100,
        available=True,
        is_ticket=True,
    )


@fixture
def other_user_entry(normal_user, open_compo, entry_zip, source_zip, image_png) -> Entry:
    """Entry belonging to another user (normal_user) in the open compo."""
    return Entry.objects.create(
        compo=open_compo,
        user=normal_user,
        name="Other User Entry",
        description="An entry by another user",
        creator="Other Creator",
        platform="Amiga",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )


@fixture
def disqualified_entry(base_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    """A disqualified entry in the votable compo."""
    return Entry.objects.create(
        compo=votable_compo,
        user=base_user,
        name="Disqualified Entry",
        description="A disqualified test entry",
        creator="DQ Creator",
        platform="PC",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
        disqualified=True,
        disqualified_reason="Rule violation",
    )


@fixture
def audio_entry(base_user, open_compo, source_zip, image_png) -> Entry:
    """Entry with an audio file (mp3 extension triggers is_audio=True)."""
    audio_file = SimpleUploadedFile("test_audio.mp3", b"fake audio data", content_type="audio/mpeg")
    entry = Entry(
        compo=open_compo,
        user=base_user,
        name="Audio Entry",
        description="An audio test entry",
        creator="Audio Creator",
        platform="PC",
        entryfile=audio_file,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )
    # Save without calling the overridden save() that triggers generate_alternates
    Entry.objects.bulk_create([entry])
    return Entry.objects.get(name="Audio Entry")

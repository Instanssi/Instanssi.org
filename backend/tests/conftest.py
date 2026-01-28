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

from django.contrib.auth.models import Permission, User
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
    ]
    return create_user(is_staff=True, permissions=permissions)


@fixture
def super_user(create_user) -> User:
    return create_user(is_staff=True, is_superuser=True)


@fixture
def event(faker) -> Event:
    event_year = faker.year()
    return Event.objects.create(
        name=f"Instanssi {event_year}",
        tag=str(event_year),
        date=date.today(),
        archived=False,
        mainurl=f"http://localhost:8000/{event_year}/",
    )


@fixture
def other_event(faker) -> Event:
    """A second event for testing cross-event validation."""
    event_year = faker.year()
    return Event.objects.create(
        name=f"Other Event {event_year}",
        tag=f"other{event_year}",
        date=date.today(),
        archived=False,
        mainurl=f"http://localhost:8000/other{event_year}/",
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
def program_event(event, faker) -> ProgrammeEvent:
    """Active program event for testing."""
    return ProgrammeEvent.objects.create(
        event=event,
        start=timezone.now() + timedelta(hours=1),
        end=timezone.now() + timedelta(hours=2),
        title=faker.sentence(nb_words=4),
        description=faker.text(max_nb_chars=256),
        presenters=faker.name(),
        place="Main Stage",
        active=True,
    )


@fixture
def inactive_program_event(event, faker) -> ProgrammeEvent:
    """Inactive program event for testing visibility."""
    return ProgrammeEvent.objects.create(
        event=event,
        start=timezone.now() + timedelta(hours=3),
        end=timezone.now() + timedelta(hours=4),
        title=faker.sentence(nb_words=4),
        description=faker.text(max_nb_chars=256),
        presenters=faker.name(),
        place="Side Stage",
        active=False,
    )


@fixture
def archived_event(faker) -> Event:
    """Archived event for testing archive visibility."""
    unique_id = faker.unique.pyint(min_value=10000, max_value=99999)
    return Event.objects.create(
        name=f"Instanssi Archive {unique_id}",
        tag=f"archive-{unique_id}",
        date=date.today() - timedelta(days=365),
        archived=True,
        mainurl=f"http://localhost:8000/archive-{unique_id}/",
    )


@fixture
def non_archived_event(faker) -> Event:
    """Non-archived event for testing archive visibility."""
    unique_id = faker.unique.pyint(min_value=10000, max_value=99999)
    return Event.objects.create(
        name=f"Instanssi Current {unique_id}",
        tag=f"current-{unique_id}",
        date=date.today(),
        archived=False,
        mainurl=f"http://localhost:8000/current-{unique_id}/",
    )


@fixture
def video_category(archived_event, faker) -> OtherVideoCategory:
    """Video category for an archived event."""
    return OtherVideoCategory.objects.create(
        event=archived_event,
        name=faker.word().capitalize() + " Videos",
    )


@fixture
def video_category_non_archived(non_archived_event, faker) -> OtherVideoCategory:
    """Video category for a non-archived event (not publicly visible)."""
    return OtherVideoCategory.objects.create(
        event=non_archived_event,
        name=faker.word().capitalize() + " Videos",
    )


@fixture
def other_video(video_category, faker) -> OtherVideo:
    """Video for an archived event."""
    return OtherVideo.objects.create(
        category=video_category,
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=256),
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )


@fixture
def other_video_non_archived(video_category_non_archived, faker) -> OtherVideo:
    """Video for a non-archived event (not publicly visible)."""
    return OtherVideo.objects.create(
        category=video_category_non_archived,
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=256),
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )


@fixture
def upcoming_compo(faker, event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Upcoming Compo",
        description="This compo cannot be participated in yet!",
        adding_end=timezone.now() + timedelta(hours=1),
        editing_end=timezone.now() + timedelta(hours=2),
        compo_start=timezone.now() + timedelta(hours=6),
        voting_start=timezone.now() + timedelta(hours=6, minutes=30),
        voting_end=timezone.now() + timedelta(hours=8),
    )


@fixture
def open_compo(faker, event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Votable Compo",
        description="Test Compo should be open for participations!",
        adding_end=timezone.now() + timedelta(minutes=30),
        editing_end=timezone.now() + timedelta(hours=1),
        compo_start=timezone.now() + timedelta(hours=2),
        voting_start=timezone.now() + timedelta(hours=3),
        voting_end=timezone.now() + timedelta(hours=8),
    )


@fixture
def votable_compo(faker, event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Votable Compo",
        description="Test Compo should be votable!",
        adding_end=timezone.now() + timedelta(hours=-6),
        editing_end=timezone.now() + timedelta(hours=-2),
        compo_start=timezone.now() + timedelta(hours=-1),
        voting_start=timezone.now() + timedelta(minutes=-30),
        voting_end=timezone.now() + timedelta(hours=8),
    )


@fixture
def closed_compo(faker, event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Closed Compo",
        description="Test Compo should be closed!",
        adding_end=timezone.now() + timedelta(hours=-6),
        editing_end=timezone.now() + timedelta(hours=-2),
        compo_start=timezone.now() + timedelta(hours=-1),
        voting_start=timezone.now() + timedelta(minutes=-30),
        voting_end=timezone.now() + timedelta(minutes=-5),
    )


@fixture
def inactive_compo(faker, event) -> Compo:
    return Compo.objects.create(
        event=event,
        name="Inactive Compo",
        description="Test Compo is not active!",
        active=False,
        adding_end=timezone.now() + timedelta(hours=1),
        editing_end=timezone.now() + timedelta(hours=2),
        compo_start=timezone.now() + timedelta(hours=3),
        voting_start=timezone.now() + timedelta(hours=4),
        voting_end=timezone.now() + timedelta(hours=8),
    )


@fixture
def editable_compo_entry(faker, base_user, open_compo, entry_zip, source_zip, image_png) -> Entry:
    return Entry.objects.create(
        compo=open_compo,
        user=base_user,
        name="Test Entry",
        description=faker.text(),
        creator=faker.name(),
        platform="Commodore 64",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )


@fixture
def closed_compo_entry(faker, base_user, closed_compo, entry_zip, source_zip, image_png) -> Entry:
    return Entry.objects.create(
        compo=closed_compo,
        user=base_user,
        name="Closed Entry",
        description=faker.text(),
        creator=faker.name(),
        platform="Commodore 64",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
        archive_score=5,
        archive_rank=1,
    )


@fixture
def votable_compo_entry(faker, base_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    return Entry.objects.create(
        compo=votable_compo,
        user=base_user,
        name="Test Entry",
        description=faker.text(),
        creator=faker.name(),
        platform="Commodore 64",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )


@fixture
def second_votable_entry(faker, normal_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    """A second entry in the votable compo."""
    return Entry.objects.create(
        compo=votable_compo,
        user=normal_user,
        name="Second Entry",
        description=faker.text(),
        creator=faker.name(),
        platform="Amiga",
        entryfile=entry_zip,
        sourcefile=source_zip,
        imagefile_original=image_png,
    )


@fixture
def third_votable_entry(faker, normal_user, votable_compo, entry_zip, source_zip, image_png) -> Entry:
    """A third entry in the votable compo."""
    return Entry.objects.create(
        compo=votable_compo,
        user=normal_user,
        name="Third Entry",
        description=faker.text(),
        creator=faker.name(),
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


@fixture
def competition(event) -> Competition:
    """Competition that hasn't started yet"""
    return Competition.objects.create(
        event=event,
        name="Test competition",
        description="Test competition is the awesomest ever!",
        participation_end=timezone.now() + timedelta(hours=1),
        start=timezone.now() + timedelta(hours=1, minutes=30),
        end=timezone.now() + timedelta(hours=8),
        score_type="p",
    )


@fixture
def started_competition(event) -> Competition:
    """Competition that has already started"""
    return Competition.objects.create(
        event=event,
        name="Started Competition",
        description="Test competition that has started",
        participation_end=timezone.now() + timedelta(hours=-1),
        start=timezone.now() + timedelta(hours=-30, minutes=-30),
        end=timezone.now() + timedelta(hours=8),
        score_type="p",
    )


@fixture
def inactive_competition(event) -> Competition:
    """Inactive competition (not shown to public)"""
    return Competition.objects.create(
        event=event,
        name="Inactive Competition",
        description="Test competition that is inactive",
        active=False,
        participation_end=timezone.now() + timedelta(hours=-1),
        start=timezone.now() + timedelta(hours=-30, minutes=-30),
        end=timezone.now() + timedelta(hours=8),
        score_type="p",
    )


@fixture
def competition_participation(faker, competition, base_user) -> CompetitionParticipation:
    return CompetitionParticipation.objects.create(
        competition=competition, user=base_user, participant_name=faker.name(), score=100.0
    )


@fixture
def started_competition_participation(faker, started_competition, base_user) -> CompetitionParticipation:
    return CompetitionParticipation.objects.create(
        competition=started_competition, user=base_user, participant_name=faker.name(), score=150.0
    )


@fixture
def other_user_competition_participation(
    faker, started_competition, normal_user
) -> CompetitionParticipation:
    """Participation belonging to another user (normal_user)."""
    return CompetitionParticipation.objects.create(
        competition=started_competition, user=normal_user, participant_name=faker.name(), score=75.0
    )


@fixture
def inactive_competition_participation(faker, inactive_competition, base_user) -> CompetitionParticipation:
    """Participation in an inactive competition."""
    return CompetitionParticipation.objects.create(
        competition=inactive_competition, user=base_user, participant_name=faker.name(), score=50.0
    )


@fixture
def store_transaction(faker, event) -> StoreTransaction:
    return StoreTransaction.objects.create(
        token=secrets.token_hex(8),
        time_created=timezone.now(),
        time_paid=timezone.now(),
        key=uuid4().hex,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
    )


@fixture
def transaction_item_a(faker, store_item, store_transaction) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        item=store_item,
        transaction=store_transaction,
        time_delivered=timezone.now(),
        purchase_price=Decimal("2.50"),
        original_price=Decimal("2.50"),
    )


@fixture
def transaction_item_b(faker, store_item, store_transaction) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        item=store_item,
        transaction=store_transaction,
        time_delivered=timezone.now(),
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
        key=uuid4().hex,
        item=store_item,
        transaction=store_transaction,
        purchase_price=store_item.price,
        original_price=store_item.price,
    )


@fixture
def unpaid_transaction(faker) -> StoreTransaction:
    """An unpaid transaction."""
    return StoreTransaction.objects.create(
        token=secrets.token_hex(8),
        time_created=timezone.now(),
        time_paid=None,  # Not paid
        key=uuid4().hex,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
    )


@fixture
def unpaid_ticket(store_item, unpaid_transaction) -> TransactionItem:
    """A ticket from an unpaid transaction."""
    return TransactionItem.objects.create(
        key=uuid4().hex,
        item=store_item,
        transaction=unpaid_transaction,
        purchase_price=store_item.price,
        original_price=store_item.price,
    )


@fixture
def non_ticket_transaction_item(variant_item, store_transaction) -> TransactionItem:
    """A transaction item for a non-ticket store item."""
    return TransactionItem.objects.create(
        key=uuid4().hex,
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
def base_store_item(faker, event, image_png) -> Callable[[], StoreItem]:
    def _inner() -> StoreItem:
        return StoreItem(
            name="Test item 1",
            event=event,
            description=faker.text(),
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
def new_transaction(faker, event) -> StoreTransaction:
    return StoreTransaction.objects.create(
        time_created=timezone.now(),
        key=uuid4().hex,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
        information=faker.text(),
    )


@fixture
def new_transaction_item(new_transaction, variant_item, store_item_variant) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        transaction=new_transaction,
        item=variant_item,
        variant=store_item_variant,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def new_transaction_item_copy(new_transaction, variant_item, store_item_variant) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        transaction=new_transaction,
        item=variant_item,
        variant=store_item_variant,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def new_transaction_item2(new_transaction, variant_item, store_item_variant2) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        transaction=new_transaction,
        item=variant_item,
        variant=store_item_variant2,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )


@fixture
def new_transaction_item3(new_transaction, store_item) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        transaction=new_transaction,
        item=store_item,
        variant=None,
        purchase_price=store_item.price,
        original_price=store_item.price,
    )


@fixture
def new_transaction_item4(new_transaction, hidden_item) -> TransactionItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        transaction=new_transaction,
        item=hidden_item,
        variant=None,
        purchase_price=hidden_item.price,
        original_price=hidden_item.price,
    )


@fixture
def receipt_params(faker) -> ReceiptParams:
    request = RequestFactory().get("/")
    p = ReceiptParams()
    p.order_number(20000)
    p.receipt_number(1000)
    p.receipt_date(timezone.now())
    p.order_date(timezone.now())
    p.first_name(faker.first_name())
    p.last_name(faker.last_name())
    p.email(faker.email())
    p.mobile(faker.phone_number())
    p.telephone(faker.phone_number())
    p.company(faker.company())
    p.street(faker.street_address())
    p.city(faker.city())
    p.postal_code(faker.postcode())
    p.country(faker.country_code())
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
        description="Competition from another event",
        participation_end=timezone.now() + timedelta(hours=1),
        start=timezone.now() + timedelta(hours=2),
        end=timezone.now() + timedelta(hours=8),
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
def other_event_transaction(other_event, faker) -> StoreTransaction:
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
        time_created=timezone.now(),
        time_paid=timezone.now(),
        key=faker.uuid4(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
    )
    TransactionItem.objects.create(
        item=store_item,
        transaction=transaction,
        key=faker.uuid4(),
        purchase_price=10,
        original_price=10,
    )
    return transaction


@fixture
def other_event_transaction_item(other_event, faker) -> TransactionItem:
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
        time_created=timezone.now(),
        time_paid=timezone.now(),
        key=faker.uuid4(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
    )
    return TransactionItem.objects.create(
        item=store_item,
        transaction=transaction,
        key=faker.uuid4(),
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

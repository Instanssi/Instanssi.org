import base64
import secrets
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.utils import timezone
from faker import Faker
from pytest import fixture
from rest_framework.test import APIClient

from Instanssi.kompomaatti.models import (
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
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem


@fixture
def faker() -> Faker:
    return Faker("fi_FI")


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
def api_client() -> APIClient:
    """Use this to test Django rest framework pages"""
    return APIClient()


@fixture
def page_client() -> Client:
    """Use this to test normal (non-api) Django pages"""
    return Client()


@fixture
def password() -> str:
    return secrets.token_hex(16)


@fixture
def auth_client(api_client, base_user, password) -> APIClient:
    api_client.login(username=base_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def staff_client(api_client, staff_user, password) -> APIClient:
    api_client.login(username=staff_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def super_client(api_client, super_user, password) -> APIClient:
    api_client.login(username=super_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def base_user(faker, password) -> User:
    return User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        password=password,
    )


@fixture
def staff_user(base_user: User) -> User:
    base_user.is_staff = True
    base_user.save(update_fields=["is_staff"])
    return base_user


@fixture
def super_user(base_user: User) -> User:
    base_user.is_superuser = True
    base_user.save(update_fields=["is_superuser"])
    return base_user


@fixture
def event(faker) -> Event:
    event_year = faker.year()
    return Event.objects.create(
        name=f"Instanssi {event_year}",
        date=timezone.now(),
        archived=False,
        mainurl=f"http://localhost:8000/{event_year}/",
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
def editable_compo_entry(faker, base_user, open_compo, entry_zip, source_zip, image_png) -> Compo:
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
def votable_compo_entry(faker, base_user, votable_compo, entry_zip, source_zip, image_png) -> Compo:
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
    )


@fixture
def competition(event) -> Competition:
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
def competition_participation(faker, competition, base_user) -> CompetitionParticipation:
    return CompetitionParticipation.objects.create(
        competition=competition, user=base_user, participant_name=faker.name()
    )


@fixture
def store_item(event) -> StoreItem:
    return StoreItem.objects.create(
        event=event,
        name="Test Product",
        description="Test Product description",
        price=1.00,
        max=10,
        available=True,
        is_ticket=True,
    )


@fixture
def store_transaction(faker, event) -> StoreItem:
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
def transaction_item_a(faker, store_item, store_transaction) -> StoreItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        item=store_item,
        transaction=store_transaction,
        time_delivered=timezone.now(),
        purchase_price=Decimal("2.50"),
        original_price=Decimal("2.50"),
    )


@fixture
def transaction_item_b(faker, store_item, store_transaction) -> StoreItem:
    return TransactionItem.objects.create(
        key=uuid4().hex,
        item=store_item,
        transaction=store_transaction,
        time_delivered=timezone.now(),
        purchase_price=Decimal("1.00"),
        original_price=Decimal("1.00"),
    )


@fixture
def ticket_vote_code(event, base_user, transaction_item_a) -> TicketVoteCode:
    return TicketVoteCode.objects.create(
        event=event,
        ticket=transaction_item_a,
        associated_to=base_user,
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
def entry_vote_group(base_user, votable_compo) -> VoteGroup:
    return VoteGroup.objects.create(
        user=base_user,
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

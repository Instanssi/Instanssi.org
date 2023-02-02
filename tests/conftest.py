import base64
import secrets
from contextlib import contextmanager
from datetime import timedelta
from decimal import Decimal
from typing import Any, Callable, Dict
from uuid import uuid4

from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
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
from Instanssi.store.models import (
    Receipt,
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    TransactionItem,
)
from Instanssi.store.utils.receipt import ReceiptParams


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
def auth_client(api_client, base_user, password) -> APIClient:
    api_client.login(username=base_user.username, password=password)
    yield api_client
    api_client.logout()


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
def staff_api_client(api_client, staff_user, password) -> APIClient:
    api_client.login(username=staff_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def super_api_client(api_client, super_user, password) -> APIClient:
    api_client.login(username=super_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def create_user(faker, password):
    def _inner(**kwargs) -> User:
        permissions = kwargs.pop("permissions", None)
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
def staff_user(create_user) -> User:
    return create_user(is_staff=True)


@fixture
def super_user(create_user) -> User:
    return create_user(is_staff=True, is_superuser=True)


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
def closed_compo_entry(faker, base_user, closed_compo, entry_zip, source_zip, image_png) -> Compo:
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
    p.transaction_url(reverse("store:ta_view", args=("1234abcd",)))
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

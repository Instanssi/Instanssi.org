import uuid
import random

from django.utils import timezone
from faker import Factory

from Instanssi.store.models import StoreItem, StoreItemVariant
from Instanssi.store.handlers import create_store_transaction
from Instanssi.common.testing.requests import FakeResponse
from Instanssi.common.testing.kompomaatti import KompomaattiTestData

fake = Factory.create('fi_FI')


class PaytrailFakeResponse(FakeResponse):
    @staticmethod
    def create_success(order_no, token):
        return {
            "orderNumber": order_no,
            "token": token,
            "url": "https://payment.paytrail.com/payment/load/token/{}".format(token)
        }

    @staticmethod
    def create_failure():
        return {
            "errorMessage": "Testing failure",
            "errorCode": "401"
        }


class StoreTestData(object):
    @staticmethod
    def create_test_item(name, event, **kwargs):
        item = StoreItem()
        item.name = name
        item.event = event
        item.description = kwargs.get('description', fake.sentences(3))
        item.price = kwargs.get('price', 20)
        item.max = kwargs.get('max', 50)
        item.available = kwargs.get('available', True)
        item.max_per_order = kwargs.get('max_per_order', 5)
        item.sort_index = kwargs.get('sort_index', 0)
        item.discount_amount = kwargs.get('discount_amount', -1)
        item.discount_percentage = kwargs.get('discount_percentage', 0)
        item.is_ticket = kwargs.get('is_ticket', False)
        item.save()
        return item

    @staticmethod
    def create_test_variants(item, amount):
        variants = []
        for i in range(amount):
            variant = StoreItemVariant()
            variant.item = item
            variant.name = "Variant {}".format(i)
            variant.save()
            variants.append(variant)
        return variants

    @staticmethod
    def create_test_transaction(items, variants):
        item = {
            "first_name": "Donald",
            "last_name": "Duck",
            "company": "None",
            "email": "donald.duck@duckburg.inv",
            "telephone": "991234567",
            "mobile": "+358991234567",
            "street": "1313 Webfoot Walk",
            "postal_code": "00000",
            "city": "Duckburg",
            "country": "US",
            "information": "Quack, damn you!",
            "items": [
                {
                    "item_id": items[0].id,
                    "variant_id": variants[0][4].id,
                    "amount": 1
                },
                {
                    "item_id": items[2].id,
                    "variant_id": variants[2][3].id,
                    "amount": 5
                }
            ]
        }
        return create_store_transaction(item)

    @staticmethod
    def create_full_started_transaction():
        event = KompomaattiTestData.create_test_event(fake.words(3))
        test_items = []
        for i in range(15 + random.randint(0, 10)):
            item = StoreTestData.create_test_item(fake.words(3), event)
            variants = StoreTestData.create_test_variants(item, random.randint(0, 5))
            for variant in variants:
                test_items.append({
                    "item_id": item.id,
                    "variant_id": variant.id,
                    "amount": random.randint(1, 10)
                })
            test_items.append({
                "item_id": item.id,
                "variant_id": None,
                "amount": random.randint(1, 10)
            })

        item = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "company": fake.company(),
            "email": fake.email(),
            "telephone": fake.phone_number(),
            "mobile": fake.phone_number(),
            "street": fake.street_address(),
            "postal_code": fake.postcode(),
            "city": fake.city(),
            "country": fake.country_code(),
            "information": fake.sentences(1),
            "items": test_items
        }
        ta = create_store_transaction(item)
        ta.token = uuid.uuid4().hex
        ta.payment_method_name = fake.words(1)
        ta.save()
        return ta

    @staticmethod
    def create_full_pending_transaction():
        ta = StoreTestData.create_full_started_transaction()
        ta.time_pending = timezone.now()
        return ta

    @staticmethod
    def create_full_paid_transaction():
        ta = StoreTestData.create_full_pending_transaction()
        ta.time_paid = timezone.now()
        return ta

    @staticmethod
    def create_full_cancelled_transaction():
        ta = StoreTestData.create_full_pending_transaction()
        ta.time_cancelled = timezone.now()
        return ta

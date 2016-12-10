# -*- coding: utf-8 -*-

from datetime import datetime
import uuid

from Instanssi.store.models import StoreItem, StoreItemVariant, TransactionItem
from Instanssi.store.handlers import begin_payment_process, create_store_transaction, validate_item,\
    TransactionException
from Instanssi.kompomaatti.models import Event

from loremipsum import get_sentences
from django.test import TestCase
from django.core.urlresolvers import reverse
import mock


class StoreTestData(object):
    @staticmethod
    def create_test_event(name):
        event = Event()
        event.name = name
        event.date = datetime.now()
        event.save()
        return event

    @staticmethod
    def create_test_item(name, event, **kwargs):
        item = StoreItem()
        item.name = name
        item.event = event
        item.description = kwargs.get('description', get_sentences(3))
        item.price = kwargs.get('price', 20)
        item.max = kwargs.get('max', 50)
        item.available = kwargs.get('available', True)
        item.max_per_order = kwargs.get('max_per_order', 5)
        item.sort_index = kwargs.get('sort_index', 0)
        item.discount_amount = kwargs.get('discount_amount', -1)
        item.discount_percentage = kwargs.get('discount_percentage', 0)
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


class FakeResponse(object):
    """
    Fake response for requests lib testing
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def json(self):
        return self.message

    @staticmethod
    def paytrail_success(order_no, token):
        return {
            "orderNumber": order_no,
            "token": token,
            "url": "https://payment.paytrail.com/payment/load/token/{}".format(token)
        }

    @staticmethod
    def paytrail_failure():
        return {
            "errorMessage": "Testing failure",
            "errorCode": "401"
        }

    @staticmethod
    def bitpay_success(order_no):
        return {
            'url': 'https://test.bitpay.com/invoice?id={}'.format(order_no),
            'status': 'new',
            'id': order_no
        }

    @staticmethod
    def bitpay_failure():
        return {}


class StoreTests(TestCase):
    def setUp(self):
        self.event = StoreTestData.create_test_event('TestEvent')
        self.items = []
        self.variants = {}
        for i in range(5):
            item = StoreTestData.create_test_item("TestItem {}".format(i), self.event, sort_index=i)
            self.items.append(item)
            self.variants[i] = StoreTestData.create_test_variants(item, 5)

        # Item 4 is not available
        self.items[4].available = False
        self.items[4].save()

        # Item 3 max product count is 0 (should not be available)
        self.items[3].max = 0
        self.items[3].save()

        # Item 2 has a discount with 5 items by 50%
        self.items[2].discount_amount = 5
        self.items[2].discount_percentage = 50
        self.items[2].save()

        # Create a test transaction
        self.transaction = StoreTestData.create_test_transaction(self.items, self.variants)

    def test_validate_item(self):
        item_tpl = {
            "item_id": self.items[0].id,
            "variant_id": None,
            "amount": 1
        }

        # Make sure too large or zero amount fails, but small enough does not
        validate_item({**item_tpl, **{"amount": 5}})
        with self.assertRaises(TransactionException):
            self.assertRaises(validate_item({**item_tpl, **{"amount": 6}}), TransactionException)
            self.assertRaises(validate_item({**item_tpl, **{"amount": 0}}), TransactionException)

        # Make sure item id checking works
        validate_item({**item_tpl, **{"item_id": self.items[0].id}})
        with self.assertRaises(TransactionException):
            validate_item({**item_tpl, **{"item_id": self.items[4].id}})  # available is False
            validate_item({**item_tpl, **{"item_id": self.items[3].id}})  # Max is 0

        # Make sure variant id checking works
        validate_item({**item_tpl, **{"item_id": self.items[1].id, "variant_id": self.variants[1][0].id}})
        validate_item({**item_tpl, **{"item_id": self.items[1].id, "variant_id": self.variants[1][4].id}})
        with self.assertRaises(TransactionException):
            # Fail if variant does not belong to the product
            validate_item({**item_tpl, **{"item_id": self.items[1].id, "variant_id": self.variants[2][0].id}})

    def test_create_transaction(self):
        ta = self.transaction

        # Make sure the data fields have been filled
        self.assertEqual(len(ta.key), 32)
        self.assertNotEqual(ta.time_created, None)
        self.assertEqual(ta.firstname, "Donald")
        self.assertEqual(ta.lastname, "Duck")
        self.assertEqual(ta.company, "None")
        self.assertEqual(ta.email, "donald.duck@duckburg.inv")
        self.assertEqual(ta.telephone, "991234567")
        self.assertEqual(ta.mobile, "+358991234567")
        self.assertEqual(ta.street, "1313 Webfoot Walk")
        self.assertEqual(ta.postalcode, "00000")
        self.assertEqual(ta.city, "Duckburg")
        self.assertEqual(ta.country, "US")
        self.assertEqual(ta.information, "Quack, damn you!")
        self.assertEqual(ta.token, '')
        self.assertEqual(ta.time_pending, None)
        self.assertEqual(ta.time_cancelled, None)
        self.assertEqual(ta.time_paid, None)
        self.assertEqual(ta.payment_method_name, '')

        # Test properties
        self.assertEqual(ta.is_cancelled, False)
        self.assertEqual(ta.is_delivered, False)
        self.assertEqual(ta.is_pending, False)
        self.assertEqual(ta.is_paid, False)
        self.assertEqual(ta.full_name, "Donald Duck")

        # Make sure this doesn't crash
        self.assertEqual(ta.qr_code.startswith("http"), True)

        # Check price functions
        self.assertEqual(ta.get_transaction_items().count(), 6)
        self.assertEqual(ta.get_total_price(), 70)  # Note discounts
        self.assertEqual(ta.get_storeitem_count(self.items[0]), 1)
        self.assertEqual(ta.get_storeitem_count(self.items[2]), 5)
        self.assertEqual(ta.get_storeitem_count(self.items[1]), 0)

        # Make sure transaction items went through
        for item in ta.get_transaction_items():
            self.assertIn(item.item.id, [self.items[0].id, self.items[2].id])
            self.assertNotEqual(item.variant, None)
            self.assertEqual(item.time_delivered, None)
            self.assertEqual(len(item.key), 32)
            self.assertEqual(item.is_delivered, False)
            self.assertEqual(item.qr_code.startswith("http"), True)

        # Check amounts (manually)
        self.assertEqual(TransactionItem.objects.filter(transaction=ta, item=self.items[0]).count(), 1)
        self.assertEqual(TransactionItem.objects.filter(transaction=ta, item=self.items[2]).count(), 5)

        # Check discount(s)
        discount_items = TransactionItem.objects.filter(transaction=ta, item=self.items[2])
        for item in discount_items:
            self.assertEqual(item.original_price, 20)
            self.assertEqual(item.purchase_price, 10)
        non_discount_item = TransactionItem.objects.get(transaction=ta, item=self.items[0])
        self.assertEqual(non_discount_item.original_price, 20)
        self.assertEqual(non_discount_item.purchase_price, 20)

    @mock.patch('Instanssi.store.utils.paytrail.requests.post',
                return_value=FakeResponse(401, FakeResponse.paytrail_failure()))
    def test_paytrail_begin_payment_process_bad_request(self, mock_post):
        result = begin_payment_process(1, self.transaction)
        self.assertEqual(result, reverse('store:pm:paytrail-failure'))
        self.assertEqual(self.transaction.token, '')

    @mock.patch('Instanssi.store.utils.paytrail.requests.post',
                return_value=FakeResponse(201, FakeResponse.paytrail_success(order_no="234246654",
                                                                             token=uuid.uuid4().hex)))
    def test_paytrail_begin_payment_process_good_request(self, mock_post):
        """"""
        result = begin_payment_process(1, self.transaction)
        self.transaction.refresh_from_db()
        self.assertNotEqual(self.transaction.token, None)
        self.assertEqual(self.transaction.payment_method_name, "Paytrail")
        self.assertEqual(result, "https://payment.paytrail.com/payment/load/token/{}".format(self.transaction.token))

    @mock.patch('Instanssi.store.utils.bitpay.requests.post',
                return_value=FakeResponse(401, FakeResponse.bitpay_failure()))
    def test_bitpay_begin_payment_process_bad_request(self, mock_post):
        result = begin_payment_process(0, self.transaction)
        self.assertEqual(result, reverse('store:pm:bitpay-failure'))

    @mock.patch('Instanssi.store.utils.bitpay.requests.post',
                return_value=FakeResponse(201, FakeResponse.bitpay_success(order_no="3456454560")))
    def test_bitpay_begin_payment_process_good_request(self, mock_post):
        result = begin_payment_process(0, self.transaction)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.token, '3456454560')
        self.assertEqual(self.transaction.payment_method_name, "Bitpay")
        self.assertEqual(result, "https://test.bitpay.com/invoice?id={}".format(self.transaction.token))

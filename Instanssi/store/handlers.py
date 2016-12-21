# -*- coding: utf-8 -*-

from datetime import datetime
import uuid
import logging

from django.db import transaction

from Instanssi.store.methods import paytrail, bitpay
from Instanssi.store.models import StoreTransaction, StoreItem, TransactionItem, StoreItemVariant

logger = logging.getLogger(__name__)


class TransactionException(Exception):
    pass


def validate_item(item):
    # First, make sure the item exists at all
    try:
        store_item = StoreItem.items_available().get(id=item['item_id'])
    except StoreItem.DoesNotExist:
        raise TransactionException("Tuotetta ei ole saatavilla")

    # Make sure the variant exists and belongs to the requested item
    if item['variant_id']:
        try:
            store_item.variants.get(id=item['variant_id'])
        except StoreItemVariant.DoesNotExist:
            raise TransactionException("Tuotetyyppiä ei ole saatavilla")

    # Make sure there are enough items in the stock to satisfy this request
    if store_item.num_available() < item['amount']:
        raise TransactionException("Tuotetta {} ei ole saatavilla riittävästi!".format(store_item.name))


def create_store_transaction(data):
    # Handle creation of the order in a transaction to avoid creating crap to db in errors
    try:
        with transaction.atomic():
            ta = StoreTransaction()
            ta.firstname = data['first_name']
            ta.lastname = data['last_name']
            ta.company = data['company']
            ta.email = data['email']
            ta.telephone = data['telephone']
            ta.mobile = data['mobile']
            ta.street = data['street']
            ta.postalcode = data['postal_code']
            ta.city = data['city']
            ta.country = data['country']
            ta.information = data['information']
            ta.time_created = datetime.now()
            ta.key = uuid.uuid4().hex
            ta.save()

            # Check items
            for item in data['items']:
                # First, make sure that the ordered item exists and is available
                store_item = StoreItem.items_available().get(pk=item['item_id'])
                store_variant = store_item.variants.get(pk=item['variant_id']) if item['variant_id'] else None

                # Find the price with discounts (if any)
                amount = item['amount']
                purchase_price = store_item.get_discounted_unit_price(amount)

                # Form the transaction item(s)
                for m in range(amount):
                    ta_item = TransactionItem()
                    ta_item.transaction = ta
                    ta_item.item = store_item
                    ta_item.variant = store_variant
                    ta_item.key = uuid.uuid4().hex
                    ta_item.purchase_price = purchase_price
                    ta_item.original_price = store_item.price
                    ta_item.save()

            return ta
    except Exception as e:
        logger.error("Unable to save store transaction: %s", str(e))
        raise


def begin_payment_process(method, ta):
    if method == 0:
        # Handle bitpay payment
        return bitpay.start_process(ta)
    else:
        # Handle paytrail payment
        return paytrail.start_process(ta)

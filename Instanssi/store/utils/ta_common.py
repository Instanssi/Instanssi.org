# -*- coding: utf-8 -*-

import logging

from django.urls import reverse
from django.utils import timezone

from Instanssi.store.utils.receipt import ReceiptParams
from Instanssi.common.misc import get_url
from Instanssi.store.models import StoreTransaction, Receipt

logger = logging.getLogger(__name__)


def handle_cancellation(ta: StoreTransaction):
    if not ta.time_cancelled:
        ta.time_cancelled = timezone.now()
        ta.save()
        logger.info('Store transaction {} cancelled.'.format(ta.id))
    else:
        logger.warning('Attempted to mark store transaction {} as cancelled twice'.format(ta.id))


def handle_pending(ta: StoreTransaction):
    if ta.time_cancelled:
        logger.warning('Cannot mark store transaction {} pending; is already cancelled.'.format(ta.id))
    elif not ta.time_pending:
        ta.time_pending = timezone.now()
        ta.save()
        logger.info('Store transaction {} paid, pending confirmation.'.format(ta.id))
    else:
        logger.warning('Attempted to mark store transaction {} as pending twice'.format(ta.id))


def handle_payment(ta: StoreTransaction):
    # If not yet marked as pending, mark it now
    if not ta.time_pending:
        ta.time_pending = timezone.now()

    # Mark as paid right away, so failures later cannot change this
    ta.time_paid = timezone.now()
    ta.save()

    # Deliver email.
    params = ReceiptParams()
    params.order_number(ta.id)
    params.order_date(ta.time_created)
    params.receipt_date(ta.time_paid)
    params.first_name(ta.firstname)
    params.last_name(ta.lastname)
    params.email(ta.email)
    params.company(ta.company)
    params.mobile(ta.mobile)
    params.telephone(ta.telephone)
    params.street(ta.street)
    params.city(ta.city)
    params.postal_code(ta.postalcode)
    params.country(ta.country)
    params.transaction_url(get_url(reverse('store:ta_view', args=(ta.key,))))

    # Add items to email
    for item, variant, purchase_price in ta.get_distinct_storeitems_and_prices():
        i_amount = ta.get_storeitem_count(item, variant=variant)
        i_name = '{}, {}'.format(item.name, variant.name) if variant else item.name
        i_id = '{}:{}'.format(item.id, variant.id) if variant else item.id
        params.add_item(i_id, i_name, purchase_price, i_amount, '0%')

    # Send mail
    try:
        receipt = Receipt.create(
            mail_to=ta.email,
            mail_from='"Instanssi" <noreply@instanssi.org>',
            subject='Instanssi.org: Kuitti tilaukselle #{}'.format(ta.id),
            params=params)
        receipt.send()
    except Exception as ex:
        logger.exception('Store: {}.'.format(ex))
        return False

    logger.info('Store transaction {} confirmed.'.format(ta.id))
    return True

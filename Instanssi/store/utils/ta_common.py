# -*- coding: utf-8 -*-

from Instanssi.common.misc import get_url
from datetime import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from Instanssi.store.models import TransactionItem
from Instanssi.store.utils.emailer import ReceiptMailer

# Logging related
import logging
logger = logging.getLogger(__name__)


def handle_cancellation(ta):
    if not ta.time_cancelled:
        ta.time_cancelled = datetime.now()
        ta.save()
        logger.info('Store transaction {} cancelled.'.format(ta.id))
    else:
        logger.warn('Attempted to mark store transaction {} as cancelled twice'.format(ta.id))


def handle_pending(ta):
    if ta.time_cancelled:
        logger.warn('Cannot mark store transaction {} pending; is already cancelled.'.format(ta.id))
    elif not ta.time_pending:
        ta.time_pending = datetime.now()
        ta.save()
        logger.info('Store transaction {} paid, pending confirmation.'.format(ta.id))
    else:
        logger.warn('Attempted to mark store transaction {} as pending twice'.format(ta.id))


def handle_payment(ta):
    # Deliver email.
    mailer = ReceiptMailer('"Instanssi" <noreply@' + settings.DOMAIN + '>', ta.email, 'Instanssi.org kuitti')
    mailer.ordernumber(ta.id)
    mailer.firstname(ta.firstname)
    mailer.lastname(ta.lastname)
    mailer.email(ta.email)
    mailer.company(ta.company)
    mailer.mobile(ta.mobile)
    mailer.telephone(ta.telephone)
    mailer.street(ta.street)
    mailer.city(ta.city)
    mailer.postalcode(ta.postalcode)
    mailer.country(ta.country)

    # Add items to email
    for item, purchase_price in ta.get_distinct_storeitems_and_prices():
        amount = ta.get_storeitem_count(item)
        mailer.add_item(item.id, item.name, purchase_price, amount)

    # Form transaction url
    transaction_url = get_url(reverse('store:ta_view', args=(ta.key,)))
    mailer.transactionurl(transaction_url)

    # Send mail
    try:
        mailer.send()
    except Exception as ex:
        logger.error('{}.'.format(ex))
        return False

    # Mark as paid
    ta.time_paid = datetime.now()
    ta.save()
    logger.info('Store transaction {} confirmed.'.format(ta.id))
    return True

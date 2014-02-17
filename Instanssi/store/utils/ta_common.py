# -*- coding: utf-8 -*-

from common.misc import get_url
from datetime import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from Instanssi.store.models import TransactionItem
from Instanssi.store.utils.emailer import ReceiptMailer

# Logging related
import logging
logger = logging.getLogger(__name__)


def handle_cancellation(ta):
    ta.time_cancelled = datetime.now()
    ta.save()

def handle_pending(ta):
    ta.time_pending = datetime.now()
    ta.save()

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
    for item in TransactionItem.get_distinct_storeitems(ta):
        amount = TransactionItem.get_transaction_item_amount(ta, item)
        mailer.add_item(item.id, item.name, item.price, amount)

    # Form transaction url
    transaction_url = get_url(reverse('store:ta_view', args=(ta.key,)))
    mailer.transactionurl(transaction_url)

    # Send mail
    try:
        mailer.send()
    except Exception as ex:
        logger.error('%s.' % (ex))
        return False

    # Mark as paid
    ta.time_paid = datetime.now()
    ta.save()
    return True

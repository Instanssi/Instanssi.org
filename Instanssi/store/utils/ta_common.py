import logging

from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from Instanssi.store import tasks
from Instanssi.store.models import Receipt, StoreTransaction
from Instanssi.store.utils.receipt import ReceiptParams

logger = logging.getLogger(__name__)


def handle_cancellation(ta: StoreTransaction) -> None:
    if not ta.time_cancelled:
        ta.time_cancelled = timezone.now()
        ta.save()
        logger.info("Store transaction %s cancelled.", ta.id)
    else:
        logger.warning("Attempted to mark store transaction %s as cancelled twice", ta.id)


def handle_pending(ta: StoreTransaction) -> None:
    if ta.time_cancelled:
        logger.warning("Cannot mark store transaction %s pending; is already cancelled.", ta.id)
    elif not ta.time_pending:
        ta.time_pending = timezone.now()
        ta.save()
        logger.info("Store transaction %s paid, pending confirmation.", ta.id)
    else:
        logger.warning("Attempted to mark store transaction %s as pending twice", ta.id)


def handle_payment(request: HttpRequest, ta: StoreTransaction) -> None:
    # Check if already paid. If so, we don't need to do anything.
    if ta.is_paid:
        logger.warning("Transaction is already paid!")
        return

    # If not yet marked as pending, mark it now
    if not ta.time_pending:
        ta.time_pending = timezone.now()

    # Mark as paid right away, so failures later cannot change this
    ta.time_paid = timezone.now()
    ta.save()

    # Create a receipt template for email
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
    params.transaction_url(request.build_absolute_uri(reverse("store:ta_view", args=(ta.key,))))

    for item, variant, purchase_price in ta.get_distinct_store_items_and_prices():
        i_amount = ta.get_store_item_count(item, variant=variant, purchase_price=purchase_price)
        i_name = f"{item.name}, {variant.name}" if variant else item.name
        i_id = f"{item.id}:{variant.id}" if variant else item.id
        params.add_item(i_id, i_name, purchase_price, i_amount, "0%")

    receipt = Receipt.create(
        mail_to=ta.email,
        mail_from='"Instanssi" <noreply@instanssi.org>',
        subject=f"Instanssi.org: Kuitti tilaukselle #{ta.id}",
        params=params,
    )
    tasks.send_receipt.delay(ta.id, receipt.id)
    logger.info("Queued receipt %d for sending.", receipt.id)
    logger.info("Store transaction %s confirmed.", ta.id)

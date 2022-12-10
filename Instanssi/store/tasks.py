import logging
from smtplib import SMTPConnectError, SMTPServerDisconnected

from celery import shared_task

from .models import Receipt, StoreTransaction, StoreTransactionEvent

log = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(SMTPServerDisconnected, SMTPConnectError),
    retry_backoff=60,
    retry_kwargs={"max_retries": 10},
)
def send_receipt(transaction_id: int, receipt_id: int) -> None:
    receipt = Receipt.objects.get(pk=receipt_id)
    transaction = StoreTransaction.objects.get(pk=transaction_id)
    log_data = dict(receipt_id=receipt_id, mail_to=receipt.mail_to)
    if receipt.is_sent:
        log.error("Attempting to resend receipt %s -- skipping.", log_data)
        return

    try:
        receipt.send()
    except Exception as e:
        log.exception("Failed to send receipt %s", log_data, exc_info=e)
        StoreTransactionEvent.log(transaction, "Receipt sending failure", {**log_data, "exception": str(e)})
        raise
    else:
        log.info("Receipt %s was sent", log_data)
        StoreTransactionEvent.log(transaction, "Receipt sent", log_data)

import logging
from smtplib import SMTPConnectError, SMTPServerDisconnected

from celery import shared_task

from .models import Receipt, StoreTransactionEvent

log = logging.getLogger(__name__)


@shared_task(  # type: ignore[untyped-decorator]
    autoretry_for=(SMTPServerDisconnected, SMTPConnectError, Receipt.DoesNotExist),
    retry_backoff=60,
    retry_kwargs={"max_retries": 10},
)
def send_receipt(receipt_id: int) -> None:
    receipt = Receipt.objects.select_related("transaction").get(pk=receipt_id)
    if receipt.is_sent:
        log.error("Receipt %d is already sent -- skipping.", receipt_id)
        return
    if not receipt.transaction:
        log.error("Receipt %d has no transaction", receipt_id)
        return

    log_data = dict(receipt_id=receipt_id, mail_to=receipt.mail_to)
    try:
        receipt.send()
    except Exception as e:
        log.exception("Failed to send receipt %s", log_data, exc_info=e)
        StoreTransactionEvent.log(
            receipt.transaction, "Receipt sending failure", {**log_data, "exception": str(e)}
        )
        raise
    else:
        log.info("Receipt %s was sent", log_data)
        StoreTransactionEvent.log(receipt.transaction, "Receipt sent", log_data)

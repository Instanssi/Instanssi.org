import pytest
from django.core import mail
from django.urls import reverse
from django.test import RequestFactory

from Instanssi.store.handlers import begin_payment_process
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import Receipt


@pytest.mark.django_db
def test_no_method_begin_payment_process_good_request(new_transaction):
    """Make sure NO_METHOD works with a good request (we should get a redirect URL)"""
    request = RequestFactory().get("/")
    result = begin_payment_process(request, PaymentMethod.NO_METHOD, new_transaction)

    # Ensure database fields got updated
    new_transaction.refresh_from_db()
    assert new_transaction.payment_method_name == "No payment"
    assert new_transaction.time_paid is not None
    assert new_transaction.time_pending is not None
    assert new_transaction.time_cancelled is None
    assert result == reverse("store:pm:no-method-success")

    # Ensure receipt exists
    assert Receipt.objects.get(mail_to=new_transaction.email)

    # Ensure mail was sent
    assert len(mail.outbox) == 1


def test_no_method_success_endpoint(page_client):
    url = reverse("store:pm:no-method-success")
    result = page_client.get(url)
    assert result.status_code == 200
    assert "store/success.html" in {tpl.name for tpl in result.templates}

import csv
import io

import pytest
from django.urls import reverse
from django.utils import timezone


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_staff,is_superuser,permissions,return_code",
    [
        (False, False, [], 403),
        (True, False, [], 403),
        (True, True, [], 200),
        (True, False, ["store.view_storetransaction"], 200),
    ],
)
def test_transaction_item_access(login_as, event, is_staff, is_superuser, permissions, return_code):
    url = reverse("manage-store:transactions_csv", args=(event.id,))
    with login_as(is_staff=is_staff, is_superuser=is_superuser, permissions=permissions) as client:
        assert client.get(url).status_code == return_code


@pytest.mark.django_db
def test_transaction_item_csv_headers(super_page_client, event):
    url = reverse("manage-store:transactions_csv", args=(event.id,))
    res = super_page_client.get(url)
    assert res.status_code == 200
    assert res.headers["Content-Disposition"] == 'attachment; filename="instanssi_entries.csv"'
    assert res.headers["Content-Type"] == "text/csv"


@pytest.mark.django_db
def test_transaction_item_csv_dump(
    super_page_client, event, new_transaction, new_transaction_item, new_transaction_item2
):
    new_transaction.time_paid = timezone.now()
    new_transaction.save()  # Convert to a paid (completed) transaction

    url = reverse("manage-store:transactions_csv", args=(event.id,))
    res = super_page_client.get(url)
    assert res.status_code == 200

    # Just ensure we can parse, and there seems to be correct amount of data.
    rows = [row for row in csv.reader(io.StringIO(res.content.decode()))]
    assert len(rows) == 3

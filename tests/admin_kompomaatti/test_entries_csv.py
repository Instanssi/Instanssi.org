import csv
import io
from unittest.mock import ANY

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_staff,is_superuser,permissions,return_code",
    [
        (False, False, [], 403),
        (True, False, [], 200),
        (True, True, [], 200),
    ],
)
def test_compo_entry_csv_access(login_as, event, is_staff, is_superuser, permissions, return_code):
    url = reverse("manage-kompomaatti:entries_csv", args=(event.id,))
    with login_as(is_staff=is_staff, is_superuser=is_superuser, permissions=permissions) as client:
        assert client.get(url).status_code == return_code


@pytest.mark.django_db
def test_compo_entry_csv_headers(super_page_client, event):
    url = reverse("manage-kompomaatti:entries_csv", args=(event.id,))
    res = super_page_client.get(url)
    assert res.status_code == 200
    assert res.headers["Content-Disposition"] == 'attachment; filename="instanssi_entries.csv"'
    assert res.headers["Content-Type"] == "text/csv"


@pytest.mark.django_db
def test_compo_entry_csv_dump(super_page_client, event, closed_compo, closed_compo_entry):
    url = reverse("manage-kompomaatti:entries_csv", args=(event.id,))
    res = super_page_client.get(url)
    assert res.status_code == 200
    rows = [row for row in csv.reader(io.StringIO(res.content.decode()))]
    assert rows == [["Closed Entry", ANY, "I", "Closed Compo"]]

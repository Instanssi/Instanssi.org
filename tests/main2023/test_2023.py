import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "site_name",
    [
        "index",
        "info",
        "english",
        "ohjelma",
        "aikataulu",
        "kompot",
        "kilpailusopimus",
        "stream",
        "saannot",
        "valot",
        "radio",
    ],
)
def test_2023_site(page_client, site_name: str):
    path = reverse(f"main2023:{site_name}")
    response = page_client.get(path)
    assert response.status_code == 200
    assert "<body>" in response.content.decode()


@pytest.mark.django_db
def test_2023_index_content(page_client):
    path = reverse(f"main2023:index")
    response = page_client.get(path)
    assert response.status_code == 200
    assert "Instanssi 2023" in response.content.decode()

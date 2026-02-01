"""Tests for file cleanup in StoreItemViewSet."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from Instanssi.store.models import StoreItem


def get_base_url(event_id: int) -> str:
    return f"/api/v2/admin/event/{event_id}/store/items/"


@pytest.fixture
def store_staff_user(create_user):
    """Staff user with store permissions."""
    permissions = [
        "store.view_storeitem",
        "store.add_storeitem",
        "store.change_storeitem",
        "store.delete_storeitem",
    ]
    return create_user(is_staff=True, permissions=permissions)


@pytest.fixture
def store_staff_client(api_client, store_staff_user, password):
    """API client authenticated as store staff."""
    api_client.login(username=store_staff_user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.fixture
def store_item_with_image(event, test_image):
    """Store item with an image file."""
    image = SimpleUploadedFile("product.png", test_image, content_type="image/png")
    return StoreItem.objects.create(
        event=event,
        name="Test Item",
        description="Test description",
        price="10.00",
        max=100,
        available=True,
        imagefile_original=image,
    )


@pytest.fixture
def store_item_without_image(event):
    """Store item without an image file."""
    return StoreItem.objects.create(
        event=event,
        name="Test Item No Image",
        description="Test description",
        price="10.00",
        max=100,
        available=True,
    )


# django-cleanup uses on_commit() hooks, so transaction=True is required


@pytest.mark.django_db(transaction=True)
def test_old_image_deleted_when_replaced(store_staff_client, store_item_with_image, test_image):
    """When uploading a new image, the old image should be deleted from storage."""
    old_file_name = store_item_with_image.imagefile_original.name
    storage = store_item_with_image.imagefile_original.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Upload a new image
    new_image = SimpleUploadedFile("new_product.png", test_image, content_type="image/png")
    url = f"{get_base_url(store_item_with_image.event_id)}{store_item_with_image.id}/"
    response = store_staff_client.patch(url, {"imagefile_original": new_image}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # New file should exist
    store_item_with_image.refresh_from_db()
    assert storage.exists(store_item_with_image.imagefile_original.name)
    assert store_item_with_image.imagefile_original.name != old_file_name


@pytest.mark.django_db(transaction=True)
def test_image_cleared_when_empty_string_sent(store_staff_client, store_item_with_image):
    """When sending empty string, the image should be cleared and deleted."""
    old_file_name = store_item_with_image.imagefile_original.name
    storage = store_item_with_image.imagefile_original.storage

    # Verify old file exists
    assert storage.exists(old_file_name)

    # Clear the image
    url = f"{get_base_url(store_item_with_image.event_id)}{store_item_with_image.id}/"
    response = store_staff_client.patch(url, {"imagefile_original": ""}, format="multipart")

    assert response.status_code == 200

    # Old file should be deleted
    assert not storage.exists(old_file_name)

    # Image field should be empty
    store_item_with_image.refresh_from_db()
    assert not store_item_with_image.imagefile_original


@pytest.mark.django_db(transaction=True)
def test_image_deleted_when_instance_deleted(store_staff_client, store_item_with_image):
    """When deleting a StoreItem, the image should be deleted from storage."""
    file_name = store_item_with_image.imagefile_original.name
    storage = store_item_with_image.imagefile_original.storage
    item_id = store_item_with_image.id

    # Verify file exists
    assert storage.exists(file_name)

    # Delete the instance
    url = f"{get_base_url(store_item_with_image.event_id)}{store_item_with_image.id}/"
    response = store_staff_client.delete(url)

    assert response.status_code == 204

    # File should be deleted from storage
    assert not storage.exists(file_name)

    # Instance should be deleted from database
    assert not StoreItem.objects.filter(id=item_id).exists()


@pytest.mark.django_db(transaction=True)
def test_image_not_deleted_when_other_fields_updated(store_staff_client, store_item_with_image):
    """When updating non-image fields, the image should not be deleted."""
    file_name = store_item_with_image.imagefile_original.name
    storage = store_item_with_image.imagefile_original.storage

    # Verify file exists
    assert storage.exists(file_name)

    # Update only the name
    url = f"{get_base_url(store_item_with_image.event_id)}{store_item_with_image.id}/"
    response = store_staff_client.patch(url, {"name": "Updated Name"}, format="multipart")

    assert response.status_code == 200

    # File should still exist
    assert storage.exists(file_name)

    # File name should not have changed
    store_item_with_image.refresh_from_db()
    assert store_item_with_image.imagefile_original.name == file_name

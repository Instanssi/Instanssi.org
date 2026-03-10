import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time

from Instanssi.api.v2.utils.entry_file_validation import _validate_file

FROZEN_TIME = "2025-01-15T12:00:00Z"


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/entries/"


# --- Unit tests for _validate_file extension logic ---


FORMATS = ["zip", "7z", "gz", "bz2"]
MAX_SIZE = 134217728


@pytest.mark.parametrize(
    "filename,expect_error",
    [
        ("entry.zip", False),
        ("entry.ZIP", False),
        ("entry.tar.gz", False),
        ("entry.tar.bz2", False),
        ("entry.TAR.GZ", False),
        ("entry.php.exe", True),
        ("entry.php.zip", False),  # last ext "zip" matches
        ("entry", True),  # no extension
        ("entry.xyz", True),
    ],
)
def test_validate_file_extension_cases(filename, expect_error):
    """Unit test for extension validation with single and double extensions."""
    file = SimpleUploadedFile(filename, b"data")
    errors = _validate_file(file, FORMATS, "zip, 7z, gz, bz2", MAX_SIZE, "128M")
    if expect_error:
        assert errors, f"Expected error for {filename}"
        assert "allowed file types" in errors[0].lower()
    else:
        assert not errors, f"Unexpected error for {filename}: {errors}"


def test_validate_file_full_double_extension_in_allow_list():
    """When 'tar.gz' is explicitly in the allow list, it matches the full extension."""
    file = SimpleUploadedFile("entry.tar.gz", b"data")
    errors = _validate_file(file, ["tar.gz"], "tar.gz", MAX_SIZE, "128M")
    assert not errors


# --- Integration tests ---


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_invalid_entry_file_format_rejected(auth_client, open_compo, source_zip, image_png):
    """Test that entry files with invalid extensions are rejected"""
    invalid_file = SimpleUploadedFile("entry.exe", b"fake content", content_type="application/octet-stream")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": invalid_file,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "entryfile" in req.data
    assert "allowed file types" in str(req.data["entryfile"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_invalid_source_file_format_rejected(auth_client, open_compo, entry_zip, image_png):
    """Test that source files with invalid extensions are rejected"""
    invalid_file = SimpleUploadedFile("source.exe", b"fake content", content_type="application/octet-stream")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": invalid_file,
        },
    )
    assert req.status_code == 400
    assert "sourcefile" in req.data
    assert "allowed file types" in str(req.data["sourcefile"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_invalid_image_file_format_rejected(auth_client, open_compo, entry_zip, source_zip, test_image):
    """Test that image files with invalid extensions are rejected"""
    # Use valid image data but with an extension not in allowed list (gif not in png|jpg)
    invalid_file = SimpleUploadedFile("image.gif", test_image, content_type="image/gif")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": invalid_file,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "imagefile_original" in req.data
    assert "allowed file types" in str(req.data["imagefile_original"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_double_extension_entry_file_rejected(auth_client, open_compo, source_zip, image_png):
    """Test that files with double extensions are rejected when neither extension matches."""
    double_ext_file = SimpleUploadedFile(
        "entry.php.exe", b"fake content", content_type="application/octet-stream"
    )
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail - double extension",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": double_ext_file,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "entryfile" in req.data
    assert "allowed file types" in str(req.data["entryfile"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_common_double_extension_accepted(auth_client, open_compo, source_zip, image_png):
    """Files with common double extensions like .tar.gz are accepted when last ext matches."""
    open_compo.formats = "zip|7z|gz|bz2"
    open_compo.save()
    tar_gz_file = SimpleUploadedFile("entry.tar.gz", b"fake content", content_type="application/gzip")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should pass - tar.gz last ext matches gz",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": tar_gz_file,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_entry_file_too_large_rejected(auth_client, open_compo, source_zip, image_png):
    """Test that entry files exceeding size limit are rejected"""
    # Set a very small size limit for testing
    open_compo.entry_sizelimit = 10  # 10 bytes
    open_compo.save()

    large_file = SimpleUploadedFile("entry.zip", b"x" * 100, content_type="application/zip")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": large_file,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "entryfile" in req.data
    assert "maximum allowed file size" in str(req.data["entryfile"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_source_file_too_large_rejected(auth_client, open_compo, entry_zip, image_png):
    """Test that source files exceeding size limit are rejected"""
    open_compo.source_sizelimit = 10  # 10 bytes
    open_compo.save()

    large_file = SimpleUploadedFile("source.zip", b"x" * 100, content_type="application/zip")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": large_file,
        },
    )
    assert req.status_code == 400
    assert "sourcefile" in req.data
    assert "maximum allowed file size" in str(req.data["sourcefile"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_image_file_too_large_rejected(auth_client, open_compo, entry_zip, source_zip, test_image):
    """Test that image files exceeding size limit are rejected"""
    open_compo.imagefile_sizelimit = 10  # 10 bytes
    open_compo.save()

    large_image = SimpleUploadedFile("image.png", test_image, content_type="image/png")
    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": large_image,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "imagefile_original" in req.data
    assert "maximum allowed file size" in str(req.data["imagefile_original"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_image_required_but_missing_rejected(auth_client, open_compo, entry_zip, source_zip):
    """Test that entries without image are rejected when image is required"""
    # Set compo to require image (thumbnail_pref=0)
    open_compo.thumbnail_pref = 0
    open_compo.save()

    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "imagefile_original" in req.data
    assert "required" in str(req.data["imagefile_original"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_image_not_allowed_but_provided_rejected(
    auth_client, open_compo, entry_zip, source_zip, image_png
):
    """Test that entries with image are rejected when image is not allowed"""
    # Set compo to not allow images (thumbnail_pref=3)
    open_compo.thumbnail_pref = 3
    open_compo.save()

    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail validation",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "imagefile_original" in req.data
    assert "not allowed" in str(req.data["imagefile_original"]).lower()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_multiple_file_errors_aggregated(auth_client, open_compo, test_image):
    """Test that errors from multiple files are returned together"""
    # Set small size limits
    open_compo.entry_sizelimit = 10
    open_compo.source_sizelimit = 10
    open_compo.save()

    large_entry = SimpleUploadedFile("entry.zip", b"x" * 100, content_type="application/zip")
    large_source = SimpleUploadedFile("source.zip", b"x" * 100, content_type="application/zip")
    # Use valid image data with wrong extension
    invalid_image = SimpleUploadedFile("image.gif", test_image, content_type="image/gif")

    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Should fail with multiple errors",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": large_entry,
            "imagefile_original": invalid_image,
            "sourcefile": large_source,
        },
    )
    assert req.status_code == 400
    # All three file fields should have errors
    assert "entryfile" in req.data
    assert "sourcefile" in req.data
    assert "imagefile_original" in req.data


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_user_entry_copied_to_image_when_configured(auth_client, open_compo, source_zip, image_png):
    """Test that entry file is copied to image when compo.is_imagefile_copied is True"""
    # Set compo to copy entry to image (thumbnail_pref=1)
    open_compo.thumbnail_pref = 1
    # Allow png as entry format for this test
    open_compo.formats = "zip|7z|gz|bz2|png"
    open_compo.save()

    base_url = get_base_url(open_compo.event_id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Entry should be copied to image",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": image_png,  # Use image as entry
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201
    # Image should have been auto-copied from entry
    assert req.data["imagefile_original_url"] is not None


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_compo_must_belong_to_event_in_url(
    auth_client, open_compo, other_event, entry_zip, source_zip, image_png
):
    """Test that compo must belong to the event specified in the URL"""
    # Try to create entry using a different event's URL
    base_url = get_base_url(other_event.id)
    req = auth_client.post(
        base_url,
        format="multipart",
        data={
            "compo": open_compo.id,  # This compo belongs to a different event
            "name": "Test Entry",
            "description": "Should fail - wrong event",
            "creator": "Test Creator",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 400
    assert "compo" in req.data

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from Instanssi.kompomaatti.enums import MediaCodec, MediaContainer
from Instanssi.kompomaatti.models import AlternateEntryFile, Entry


@pytest.mark.django_db
def test_m3u8_strips_crlf_from_creator_and_name(
    page_client, base_user, archived_compo, archived_event, entry_zip
):
    """Entries with line breaks in name/creator are sanitized in M3U8 output."""
    entry = Entry.objects.create(
        compo=archived_compo,
        user=base_user,
        name="Evil\r\nEntry",
        description="Test",
        creator="Evil\nCreator",
        entryfile=entry_zip,
    )
    AlternateEntryFile.objects.create(
        entry=entry,
        codec=MediaCodec.OPUS,
        container=MediaContainer.WEBM,
        file=SimpleUploadedFile("test.webm", b"fake webm content"),
    )

    response = page_client.get(reverse("archive:entries_m3u8", args=[archived_event.id]))
    assert response.status_code == 200

    content = response.content.decode()
    # The EXTINF line should not contain raw \r or \n from the entry fields
    lines = content.split("\r\n")
    extinf_lines = [line for line in lines if line.startswith("#EXTINF")]
    assert len(extinf_lines) == 1
    assert "EvilCreator" in extinf_lines[0]
    assert "EvilEntry" in extinf_lines[0]
    # No injected extra lines from the entry fields
    assert "\r\nEntry" not in content
    assert "\nCreator" not in content

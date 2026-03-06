import logging
from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from Instanssi.kompomaatti.enums import MediaCodec, MediaContainer
from Instanssi.kompomaatti.models import AlternateEntryFile, Entry
from Instanssi.kompomaatti.tasks import generate_alternate_audio_files


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_generate_alternate_audio_files_success(audio_entry, caplog):
    """Test successful audio file conversion creates an AlternateEntryFile."""
    caplog.set_level(logging.INFO)

    # Mock ffmpeg pipeline
    with (
        mock.patch("Instanssi.kompomaatti.tasks.ffmpeg.input") as mock_input,
        mock.patch("Instanssi.kompomaatti.tasks.temp_file") as mock_temp_file,
    ):
        # Set up mocks
        mock_pipeline = mock.MagicMock()
        mock_input.return_value.audio = mock_pipeline
        mock_output = mock.MagicMock()
        mock_pipeline.return_value = mock_output
        mock_output.global_args.return_value.run = mock.MagicMock()

        # Create a fake output file
        mock_temp_file.return_value.__enter__ = mock.MagicMock(return_value="/tmp/fake_output.webm")
        mock_temp_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        # Mock open to return fake audio data
        with mock.patch("builtins.open", mock.mock_open(read_data=b"converted audio data")):
            with mock.patch("Instanssi.kompomaatti.tasks.ffmpeg.output", mock_output):
                mock_output.return_value = mock_output
                generate_alternate_audio_files.delay(
                    audio_entry.id, int(MediaCodec.OPUS), int(MediaContainer.WEBM)
                )

        # Verify AlternateEntryFile was created
        alt = AlternateEntryFile.objects.filter(
            entry=audio_entry, codec=MediaCodec.OPUS, container=MediaContainer.WEBM
        ).first()
        assert alt is not None
        assert alt.entry == audio_entry


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_generate_alternate_audio_files_skips_non_audio(editable_compo_entry, caplog):
    """Test that non-audio files are skipped without error."""
    caplog.set_level(logging.ERROR)

    generate_alternate_audio_files.delay(
        editable_compo_entry.id, int(MediaCodec.OPUS), int(MediaContainer.WEBM)
    )

    # Verify no AlternateEntryFile was created
    assert AlternateEntryFile.objects.filter(entry=editable_compo_entry).count() == 0

    # Verify error was logged
    assert any("Input file is not an audio file" in r.message for r in caplog.records)


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_generate_alternate_audio_files_missing_entry(caplog):
    """Test that missing entry triggers retry (Entry.DoesNotExist)."""
    caplog.set_level(logging.ERROR)

    # Call with non-existent entry ID - should retry and eventually fail
    with pytest.raises(Entry.DoesNotExist):
        generate_alternate_audio_files(999999, int(MediaCodec.OPUS), int(MediaContainer.WEBM))


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_generate_alternate_audio_files_updates_existing(audio_entry, test_zip):
    """Test that existing alternate file is updated (not duplicated)."""
    # Create an existing AlternateEntryFile
    existing_file = SimpleUploadedFile("old_alternate.webm", test_zip, content_type="audio/webm")
    existing_alt = AlternateEntryFile.objects.create(
        entry=audio_entry,
        codec=MediaCodec.OPUS,
        container=MediaContainer.WEBM,
        file=existing_file,
    )
    original_created_at = existing_alt.created_at

    # Mock ffmpeg pipeline
    with (
        mock.patch("Instanssi.kompomaatti.tasks.ffmpeg.input") as mock_input,
        mock.patch("Instanssi.kompomaatti.tasks.temp_file") as mock_temp_file,
        mock.patch("Instanssi.kompomaatti.tasks.ffmpeg.output") as mock_ffmpeg_output,
    ):
        # Set up mocks
        mock_pipeline = mock.MagicMock()
        mock_input.return_value.audio = mock_pipeline
        mock_output = mock.MagicMock()
        mock_ffmpeg_output.return_value = mock_output
        mock_output.global_args.return_value.run = mock.MagicMock()

        # Create a fake output file
        mock_temp_file.return_value.__enter__ = mock.MagicMock(return_value="/tmp/fake_output.webm")
        mock_temp_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        # Mock open to return fake audio data
        with mock.patch("builtins.open", mock.mock_open(read_data=b"new converted audio data")):
            generate_alternate_audio_files.delay(
                audio_entry.id, int(MediaCodec.OPUS), int(MediaContainer.WEBM)
            )

    # Verify only one AlternateEntryFile exists (updated, not duplicated)
    alts = AlternateEntryFile.objects.filter(
        entry=audio_entry, codec=MediaCodec.OPUS, container=MediaContainer.WEBM
    )
    assert alts.count() == 1

    # Verify updated_at was changed
    updated_alt = alts.first()
    assert updated_alt.updated_at > original_created_at


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_generate_alternate_audio_files_ffmpeg_error(audio_entry, caplog):
    """Test that ffmpeg errors are logged and re-raised."""
    caplog.set_level(logging.ERROR)

    with (
        mock.patch("Instanssi.kompomaatti.tasks.ffmpeg.input") as mock_input,
        mock.patch("Instanssi.kompomaatti.tasks.temp_file") as mock_temp_file,
        mock.patch("Instanssi.kompomaatti.tasks.ffmpeg.output") as mock_ffmpeg_output,
    ):
        # Set up mocks
        mock_pipeline = mock.MagicMock()
        mock_input.return_value.audio = mock_pipeline
        mock_output = mock.MagicMock()
        mock_ffmpeg_output.return_value = mock_output
        mock_output.global_args.return_value.run.side_effect = Exception("ffmpeg failed")

        # Create a fake output file
        mock_temp_file.return_value.__enter__ = mock.MagicMock(return_value="/tmp/fake_output.webm")
        mock_temp_file.return_value.__exit__ = mock.MagicMock(return_value=False)

        with pytest.raises(Exception, match="ffmpeg failed"):
            generate_alternate_audio_files(audio_entry.id, int(MediaCodec.OPUS), int(MediaContainer.WEBM))

    # Verify error was logged
    assert any("Unable to convert" in r.message for r in caplog.records)

    # Verify no AlternateEntryFile was created
    assert AlternateEntryFile.objects.filter(entry=audio_entry).count() == 0

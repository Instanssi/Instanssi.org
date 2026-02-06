import stat
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path

from stream_zip import NO_COMPRESSION_64, MemberFile, stream_zip


def generate_zip_stream(
    files: Iterable[tuple[str, Path]],
) -> Iterator[bytes]:
    """Generate a streaming ZIP archive.

    Args:
        files: Iterable of (archive_name, file_path) tuples.
            archive_name: Path within the archive (e.g., "dir/file.txt")
            file_path: Path to the file on disk

    Yields:
        Chunks of ZIP data.
    """

    def _member_files() -> Iterator[MemberFile]:
        for arcname, file_path in files:
            file_stat = file_path.stat()
            modified_at = datetime.fromtimestamp(file_stat.st_mtime, tz=UTC)
            perms = stat.S_IFREG | 0o644

            def _read_chunks(p: Path = file_path) -> Iterator[bytes]:
                with p.open("rb") as f:
                    while chunk := f.read(65536):
                        yield chunk

            yield arcname, modified_at, perms, NO_COMPRESSION_64, _read_chunks()

    yield from stream_zip(_member_files())

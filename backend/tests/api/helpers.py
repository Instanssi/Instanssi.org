from yarl import URL


class FileURL:
    """URL matcher that compares only the path portion."""

    def __init__(self, expected_path: str):
        self.expected_path = expected_path

    def __eq__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        return URL(other).path == self.expected_path

    def __repr__(self):
        return f"FileURL({self.expected_path!r})"


def file_url(field) -> FileURL:
    """Create a FileURL matcher from a Django file field."""
    return FileURL(field.url)

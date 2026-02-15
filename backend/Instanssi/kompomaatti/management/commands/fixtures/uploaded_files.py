from datetime import datetime, timezone
from typing import Any

# Uploaded files fixture data
# Each entry references an event_pk and user_username, with a description and file type

uploaded_files: list[dict[str, Any]] = [
    {
        "event_pk": 23,  # Instanssi 2024
        "user_username": "admin",
        "description": "Sponsor logo - Demoscene.fi",
        "file_type": "image",
        "date": datetime(2024, 2, 15, 10, 30, 0, tzinfo=timezone.utc),
    },
    {
        "event_pk": 1,
        "user_username": "admin",
        "description": "Event poster draft",
        "file_type": "image",
        "date": datetime(2024, 2, 16, 14, 45, 0, tzinfo=timezone.utc),
    },
    {
        "event_pk": 1,
        "user_username": "testuser1",
        "description": "Rules document backup",
        "file_type": "archive",
        "date": datetime(2024, 2, 17, 9, 0, 0, tzinfo=timezone.utc),
    },
    {
        "event_pk": 25,  # Instanssi 2026
        "user_username": "admin",
        "description": "Sponsor logo - Scene.org",
        "file_type": "image",
        "date": datetime(2025, 1, 10, 11, 0, 0, tzinfo=timezone.utc),
    },
    {
        "event_pk": 2,
        "user_username": "admin",
        "description": "Press kit materials",
        "file_type": "archive",
        "date": datetime(2025, 1, 12, 16, 30, 0, tzinfo=timezone.utc),
    },
]

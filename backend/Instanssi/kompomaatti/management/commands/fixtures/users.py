"""Test users for kompomaatti"""

from typing import Any

users: list[dict[str, Any]] = [
    {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "first_name": "Test",
        "last_name": "User",
        "is_staff": False,
        "is_superuser": False,
        "otherinfo": "IRC: testuser1 @ IRCNet\nDiscord: testuser#1234",
    },
    {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "first_name": "Another",
        "last_name": "Tester",
        "is_staff": False,
        "is_superuser": False,
        "otherinfo": "IRC: testuser2 @ QuakeNet\nMatrix: @testuser2:matrix.org",
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "voter1",
        "email": "voter1@example.com",
        "first_name": "Voter",
        "last_name": "One",
        "is_staff": False,
        "is_superuser": False,
        "otherinfo": "IRC: voter1 @ IRCNet",
    },
    {
        "username": "voter2",
        "email": "voter2@example.com",
        "first_name": "Voter",
        "last_name": "Two",
        "is_staff": False,
        "is_superuser": False,
        "otherinfo": "Discord: voter2#5678",
    },
]

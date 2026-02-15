"""Test votes for kompomaatti"""

from typing import Any

# Vote groups - each represents one user's votes for one compo
vote_groups: list[dict[str, Any]] = [
    {
        "user_username": "voter1",
        "compo_name": "Graphics",
        "compo_event_pk": 23,
    },
    {
        "user_username": "voter2",
        "compo_name": "Graphics",
        "compo_event_pk": 23,
    },
    {
        "user_username": "voter1",
        "compo_name": "Music",
        "compo_event_pk": 23,
    },
    {
        "user_username": "voter2",
        "compo_name": "Music",
        "compo_event_pk": 23,
    },
    {
        "user_username": "testuser1",
        "compo_name": "Music",
        "compo_event_pk": 23,
    },
]

# Individual votes - rankings within each group
# Format: (group_index, entry_name, rank)
votes: list[dict[str, Any]] = [
    # voter1's votes for Graphics compo (event 23)
    {
        "group_index": 0,  # References vote_groups[0]
        "entry_name": "Sunset Dreams",
        "rank": 1,  # First place in voter1's ranking
    },
    {
        "group_index": 0,
        "entry_name": "Abstract Patterns",
        "rank": 2,
    },
    {
        "group_index": 0,
        "entry_name": "Cyberpunk City",
        "rank": 3,
    },
    # voter2's votes for Graphics compo (event 23)
    {
        "group_index": 1,  # References vote_groups[1]
        "entry_name": "Cyberpunk City",
        "rank": 1,
    },
    {
        "group_index": 1,
        "entry_name": "Sunset Dreams",
        "rank": 2,
    },
    {
        "group_index": 1,
        "entry_name": "Abstract Patterns",
        "rank": 3,
    },
    # voter1's votes for Music compo (event 23)
    {
        "group_index": 2,  # References vote_groups[2]
        "entry_name": "Electric Dreams",
        "rank": 1,
    },
    {
        "group_index": 2,
        "entry_name": "Chiptune Madness",
        "rank": 2,
    },
    {
        "group_index": 2,
        "entry_name": "Ambient Space",
        "rank": 3,
    },
    # voter2's votes for Music compo (event 23)
    {
        "group_index": 3,  # References vote_groups[3]
        "entry_name": "Chiptune Madness",
        "rank": 1,
    },
    {
        "group_index": 3,
        "entry_name": "Electric Dreams",
        "rank": 2,
    },
    {
        "group_index": 3,
        "entry_name": "Ambient Space",
        "rank": 3,
    },
    # testuser1's votes for Music compo (event 23)
    {
        "group_index": 4,  # References vote_groups[4]
        "entry_name": "Electric Dreams",
        "rank": 1,
    },
    {
        "group_index": 4,
        "entry_name": "Ambient Space",
        "rank": 2,
    },
    {
        "group_index": 4,
        "entry_name": "Chiptune Madness",
        "rank": 3,
    },
]

"""Test vote code requests for kompomaatti"""

from typing import Any

vote_code_requests: list[dict[str, Any]] = [
    # Pending request
    {
        "event_pk": 25,  # Instanssi 2026
        "user_username": "testuser1",
        "text": "Hei! Haluaisin äänioikeuden tulevaan tapahtumaan. Olen osallistunut aikaisempiinkin Instansseihin ja aion tulla paikalle.",
        "status": 0,  # Pending
    },
    # Accepted request
    {
        "event_pk": 25,
        "user_username": "voter1",
        "text": "Pyysin jo lipun verkkokaupasta, voisinko saada äänioikeuden?",
        "status": 1,  # Accepted
    },
    # Rejected request
    {
        "event_pk": 25,
        "user_username": "voter2",
        "text": "äänestyskoodi pls",
        "status": 2,  # Rejected - too short/lazy request
    },
    # Accepted request from previous event
    {
        "event_pk": 23,  # Instanssi 2024
        "user_username": "testuser2",
        "text": "Osallistun tapahtumaan ja haluaisin äänestää kompoissa.",
        "status": 1,  # Accepted
    },
]

# Note: TicketVoteCode entries are typically created from store tickets
# For testing purposes, we won't create them here as they require
# store.TransactionItem objects which are from a different app
ticket_vote_codes: list[dict[str, Any]] = [
    # These would be created when actual ticket purchases are made
    # or when admins manually grant voting rights
]

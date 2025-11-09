"""Test blog entries for events"""

from datetime import UTC, datetime

blog_entries = [
    # Blog entries for Instanssi 2026 (upcoming event)
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Instanssi 2026 - Registration Open!",
        "text": """<p>We are excited to announce that registration for Instanssi 2026 is now open!</p>
<p>Join us February 26-28, 2026 for another amazing event featuring:</p>
<ul>
<li>Graphics, Music, and Demo competitions</li>
<li>Speed Coding and Speedrun challenges</li>
<li>Live streaming and voting</li>
<li>Community hangout and networking</li>
</ul>
<p>Visit the registration page to sign up now. Early bird tickets available!</p>""",
        "date": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Compo Schedule Released",
        "text": """<p>The complete schedule for Instanssi 2026 compos is now available!</p>
<p><strong>Friday, February 27:</strong></p>
<ul>
<li>18:00 - Graphics compo</li>
<li>19:00 - Music compo</li>
<li>20:00 - Demo compo</li>
</ul>
<p><strong>Saturday, February 28:</strong></p>
<ul>
<li>14:00 - Speed Coding competition</li>
<li>14:00 - Speedrun Challenge</li>
</ul>
<p>Entry submissions close February 22, so get your work ready!</p>""",
        "date": datetime(2026, 2, 1, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Draft: Venue Details",
        "text": """<p>This is a draft blog entry with venue information.</p>
<p>Will be published closer to the event date.</p>""",
        "date": datetime(2026, 2, 10, 15, 0, 0, tzinfo=UTC),
        "public": False,  # Draft entry
    },
    # Blog entries for Instanssi 2024 (archived event)
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Instanssi 2024 - Thank You!",
        "text": """<p>Instanssi 2024 is now over! Thank you to everyone who participated.</p>
<p>We had amazing entries in all categories and great turnout for the competitions.</p>
<p>Results are now available in the archive. Congratulations to all winners!</p>
<p>See you next year!</p>""",
        "date": datetime(2024, 3, 2, 18, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Final Day - Voting Closes Soon",
        "text": """<p>Today is the final day of Instanssi 2024!</p>
<p>Voting closes at 12:00 today. Make sure to cast your votes for your favorite entries.</p>
<p>Results will be announced this evening. Stay tuned!</p>""",
        "date": datetime(2024, 3, 2, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Instanssi 2024 Kicks Off!",
        "text": """<p>Instanssi 2024 has officially started!</p>
<p>Compos begin tonight. Graphics compo at 18:00, Music at 19:00.</p>
<p>Live stream is available on our website. Don't miss it!</p>""",
        "date": datetime(2024, 3, 1, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    # Blog entries for Instanssi 2023
    {
        "event_pk": 22,
        "user_username": "admin",
        "title": "Instanssi 2023 - Thanks for Coming!",
        "text": """<p>Another successful Instanssi is in the books!</p>
<p>We had record participation this year with amazing demos, graphics, and music entries.</p>
<p>All results are now published in the archive section.</p>
<p>Special thanks to our sponsors and volunteers who made this possible!</p>""",
        "date": datetime(2023, 3, 5, 20, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 22,
        "user_username": "admin",
        "title": "Welcome to Instanssi 2023",
        "text": """<p>Instanssi 2023 is here! Welcome to all attendees.</p>
<p>Check out the schedule and don't forget to vote after watching the compo entries.</p>
<p>Have a great time!</p>""",
        "date": datetime(2023, 3, 3, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    # Blog entries for Instanssi 2021
    {
        "event_pk": 19,
        "user_username": "admin",
        "title": "Instanssi 2021 Wrap-Up",
        "text": """<p>What an amazing event! Instanssi 2021 was a huge success.</p>
<p>Thanks to everyone who submitted entries and participated in voting.</p>
<p>See the archive for full results and all the incredible entries we received.</p>""",
        "date": datetime(2021, 3, 7, 16, 0, 0, tzinfo=UTC),
        "public": True,
    },
]

"""Test competitions for kompomaatti"""

from datetime import UTC, datetime

competitions = [
    # Active competition for 2026
    {
        "event_pk": 25,  # Instanssi 2026
        "name": "Speed Coding",
        "description": """<p>Koodauskilpailu jossa ratkaistaan algoritmisia ongelmia mahdollisimman nopeasti!</p>
<p>Kilpailu kestää <strong>2 tuntia</strong> ja sisältää useita tehtäviä.
Pisteet lasketaan ratkaistujen tehtävien määrän ja käytetyn ajan perusteella.</p>
<p><em>Kieli vapaa</em> - käytä mitä tahansa ohjelmointikieltä.</p>""",
        "participation_end": datetime(2026, 2, 26, 12, 0, 0, tzinfo=UTC),
        "start": datetime(2026, 2, 27, 14, 0, 0, tzinfo=UTC),
        "end": datetime(2026, 2, 27, 16, 0, 0, tzinfo=UTC),
        "score_type": "p",  # points
        "score_sort": 0,  # Highest score wins
        "show_results": False,
        "active": True,
        "hide_from_archive": False,
    },
    {
        "event_pk": 25,
        "name": "Speedrun Challenge",
        "description": """<p>Pelaa läpi klassikkopeli mahdollisimman nopeasti!</p>
<p>Peli ilmoitetaan kilpailun alkaessa.
Kaikki käyttävät samaa platformia ja versiota.</p>
<p><strong>Pisteet = aika sekunteina</strong> (pienin voittaa!)</p>""",
        "participation_end": datetime(2026, 2, 26, 18, 0, 0, tzinfo=UTC),
        "start": datetime(2026, 2, 28, 14, 0, 0, tzinfo=UTC),
        "end": datetime(2026, 2, 28, 16, 0, 0, tzinfo=UTC),
        "score_type": "sek",  # seconds
        "score_sort": 1,  # Lowest score wins
        "show_results": False,
        "active": True,
        "hide_from_archive": False,
    },
    # Archived competition from 2024
    {
        "event_pk": 23,  # Instanssi 2024
        "name": "Retro Gaming",
        "description": "<p>Retro gaming <strong>high score</strong> competition</p>",
        "participation_end": datetime(2024, 2, 28, 18, 0, 0, tzinfo=UTC),
        "start": datetime(2024, 3, 1, 14, 0, 0, tzinfo=UTC),
        "end": datetime(2024, 3, 1, 18, 0, 0, tzinfo=UTC),
        "score_type": "p",
        "score_sort": 0,  # Highest score wins
        "show_results": True,
        "active": True,
        "hide_from_archive": False,
    },
]

competition_participations = [
    # Speed Coding participations (2026 - no scores yet)
    {
        "competition_name": "Speed Coding",
        "competition_event_pk": 25,
        "user_username": "testuser1",
        "participant_name": "CodeNinja",
        "score": 0,
        "disqualified": False,
        "disqualified_reason": "",
    },
    {
        "competition_name": "Speed Coding",
        "competition_event_pk": 25,
        "user_username": "testuser2",
        "participant_name": "AlgoMaster",
        "score": 0,
        "disqualified": False,
        "disqualified_reason": "",
    },
    # Speedrun Challenge participations (2026 - no scores yet)
    {
        "competition_name": "Speedrun Challenge",
        "competition_event_pk": 25,
        "user_username": "voter1",
        "participant_name": "SpeedRunner99",
        "score": 0,
        "disqualified": False,
        "disqualified_reason": "",
    },
    # Retro Gaming participations (2024 - with scores)
    {
        "competition_name": "Retro Gaming",
        "competition_event_pk": 23,
        "user_username": "testuser1",
        "participant_name": "HighScoreHero",
        "score": 125000,
        "disqualified": False,
        "disqualified_reason": "",
    },
    {
        "competition_name": "Retro Gaming",
        "competition_event_pk": 23,
        "user_username": "voter1",
        "participant_name": "ArcadeMaster",
        "score": 98500,
        "disqualified": False,
        "disqualified_reason": "",
    },
    {
        "competition_name": "Retro Gaming",
        "competition_event_pk": 23,
        "user_username": "voter2",
        "participant_name": "RetroGamer",
        "score": 87200,
        "disqualified": False,
        "disqualified_reason": "",
    },
    {
        "competition_name": "Retro Gaming",
        "competition_event_pk": 23,
        "user_username": "testuser2",
        "participant_name": "DisqualifiedUser",
        "score": 150000,
        "disqualified": True,
        "disqualified_reason": "Used external assistance/cheats during the competition.",
    },
]

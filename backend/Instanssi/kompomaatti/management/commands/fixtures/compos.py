"""Test compos for kompomaatti"""

from datetime import UTC, datetime
from typing import Any

# Compos for the active event (2026)
compos_2026: list[dict[str, Any]] = [
    {
        "event_pk": 25,  # Instanssi 2026
        "name": "Graphics",
        "description": """Grafiikkakompossa kilpaillaan parhaasta kuvasta!

Tekniikat ovat vapaat - voit käyttää mitä tahansa ohjelmaa tai tekniikkaa.
Piirrä, maalaa, renderöi tai photoshoppaa - vapaasti valittavissa!

Tiedostomuoto: PNG tai JPG
Maksimikoko: Ei rajoitusta (järki käteen)""",
        "adding_end": datetime(2026, 2, 22, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2026, 2, 25, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2026, 2, 27, 18, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2026, 2, 27, 18, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 10 * 1024 * 1024,  # 10 MB
        "source_sizelimit": 50 * 1024 * 1024,  # 50 MB
        "formats": "png|jpg|jpeg",
        "source_formats": "zip|7z|gz|bz2|rar",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": False,
        "entry_view_type": 2,  # Image only
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 1,  # Use entry file as thumbnail
    },
    {
        "event_pk": 25,
        "name": "Music",
        "description": """Musiikkikompossa etsitään parasta ääniraitaa!

Tyylilaji on vapaa - techno, ambient, rock, chiptune, mikä vain käy.
Maksimipituus: 5 minuuttia

Tiedostomuodot: MP3, OGG, FLAC, WAV tai MOD/XM/IT
Lähdekoodit: Tracker-tiedostot, projektifileet yms. suositeltavia!""",
        "adding_end": datetime(2026, 2, 22, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2026, 2, 25, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2026, 2, 27, 19, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2026, 2, 27, 19, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 50 * 1024 * 1024,  # 50 MB
        "source_sizelimit": 100 * 1024 * 1024,  # 100 MB
        "formats": "mp3|ogg|flac|wav|mod|xm|it|s3m",
        "source_formats": "zip|7z|gz|bz2|rar",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": False,
        "entry_view_type": 1,  # Youtube first, then image
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 2,  # Optional thumbnail
    },
    {
        "event_pk": 25,
        "name": "Demo",
        "description": """Demokompossa etsitään parasta real-time audiovisuaalista esitystä!

Platformi vapaa - PC, Amiga, C64, web, mitä tahansa.
Maksimipituus: Ei rajoitusta (suositus 3-10min)

Huom! Jos entry vaatii erityisiä ajamisohjeita tai tiettyä laitteistoa,
mainitse ne kuvauksessa.""",
        "adding_end": datetime(2026, 2, 22, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2026, 2, 25, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2026, 2, 27, 20, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2026, 2, 27, 20, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 200 * 1024 * 1024,  # 200 MB
        "source_sizelimit": 200 * 1024 * 1024,  # 200 MB
        "formats": "zip|7z|gz|bz2|rar",
        "source_formats": "zip|7z|gz|bz2|rar",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": False,
        "entry_view_type": 1,  # Youtube first, then image
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 0,  # Require separate thumbnail
    },
]

# Archived compos from past events with voting closed
compos_2024: list[dict[str, Any]] = [
    {
        "event_pk": 23,  # Instanssi 2024 (Event date: Feb 29)
        "name": "Graphics",
        "description": "Archived graphics compo from 2024",
        "adding_end": datetime(2024, 2, 27, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2024, 2, 28, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2024, 3, 1, 18, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2024, 3, 1, 18, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2024, 3, 2, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 10 * 1024 * 1024,
        "source_sizelimit": 50 * 1024 * 1024,
        "formats": "png|jpg|jpeg",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 2,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 1,
    },
    {
        "event_pk": 23,
        "name": "Music",
        "description": "Archived music compo from 2024",
        "adding_end": datetime(2024, 2, 27, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2024, 2, 28, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2024, 3, 1, 19, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2024, 3, 1, 19, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2024, 3, 2, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 50 * 1024 * 1024,
        "source_sizelimit": 100 * 1024 * 1024,
        "formats": "mp3|ogg|flac|wav|mod|xm|it",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 1,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 2,
    },
]

# Archived compos from 2023
compos_2023: list[dict[str, Any]] = [
    {
        "event_pk": 22,  # Instanssi 2023 (Event date: March 3)
        "name": "Graphics",
        "description": "Archived graphics compo from 2023",
        "adding_end": datetime(2023, 3, 1, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2023, 3, 2, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2023, 3, 3, 18, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2023, 3, 3, 18, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2023, 3, 5, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 10 * 1024 * 1024,
        "source_sizelimit": 50 * 1024 * 1024,
        "formats": "png|jpg|jpeg",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 2,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 1,
    },
    {
        "event_pk": 22,
        "name": "Music",
        "description": "Archived music compo from 2023",
        "adding_end": datetime(2023, 3, 1, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2023, 3, 2, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2023, 3, 3, 19, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2023, 3, 3, 19, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2023, 3, 5, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 50 * 1024 * 1024,
        "source_sizelimit": 100 * 1024 * 1024,
        "formats": "mp3|ogg|flac|wav|mod|xm|it",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 1,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 2,
    },
    {
        "event_pk": 22,
        "name": "Demo",
        "description": "Archived demo compo from 2023",
        "adding_end": datetime(2023, 3, 1, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2023, 3, 2, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2023, 3, 3, 20, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2023, 3, 3, 20, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2023, 3, 5, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 200 * 1024 * 1024,
        "source_sizelimit": 200 * 1024 * 1024,
        "formats": "zip|7z|gz|bz2",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 1,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 0,
    },
]

# Archived compos from 2021
compos_2021: list[dict[str, Any]] = [
    {
        "event_pk": 19,  # Instanssi 2021 (Event date: March 5)
        "name": "Graphics",
        "description": "Archived graphics compo from 2021",
        "adding_end": datetime(2021, 3, 3, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2021, 3, 4, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2021, 3, 5, 18, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2021, 3, 5, 18, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2021, 3, 7, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 10 * 1024 * 1024,
        "source_sizelimit": 50 * 1024 * 1024,
        "formats": "png|jpg|jpeg",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 2,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 1,
    },
    {
        "event_pk": 19,
        "name": "Music",
        "description": "Archived music compo from 2021",
        "adding_end": datetime(2021, 3, 3, 23, 59, 0, tzinfo=UTC),
        "editing_end": datetime(2021, 3, 4, 12, 0, 0, tzinfo=UTC),
        "compo_start": datetime(2021, 3, 5, 19, 0, 0, tzinfo=UTC),
        "voting_start": datetime(2021, 3, 5, 19, 30, 0, tzinfo=UTC),
        "voting_end": datetime(2021, 3, 7, 12, 0, 0, tzinfo=UTC),
        "entry_sizelimit": 50 * 1024 * 1024,
        "source_sizelimit": 100 * 1024 * 1024,
        "formats": "mp3|ogg|flac|wav|mod|xm|it",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "active": True,
        "show_voting_results": True,
        "entry_view_type": 1,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 2,
    },
]

# All compos
compos = compos_2026 + compos_2024 + compos_2023 + compos_2021

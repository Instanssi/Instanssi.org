"""Test video categories and videos for events"""

# Video categories for archived events
video_categories = [
    # Instanssi 2024
    {
        "event_pk": 23,
        "name": "Seminaarit",
    },
    {
        "event_pk": 23,
        "name": "Live-esitykset",
    },
    {
        "event_pk": 23,
        "name": "Haastattelut",
    },
    # Instanssi 2023
    {
        "event_pk": 22,
        "name": "Seminaarit",
    },
    {
        "event_pk": 22,
        "name": "Behind the Scenes",
    },
    # Instanssi 2026 (upcoming event, for testing)
    {
        "event_pk": 25,
        "name": "Ennakkovideot",
    },
]

# Videos linked to categories
videos = [
    # Instanssi 2024 - Seminaarit
    {
        "category_event_pk": 23,
        "category_name": "Seminaarit",
        "name": "Demoscene in 2024",
        "description": "A look at the current state of the demoscene and where it's heading. "
        "Presented by veteran scener with 20+ years of experience.",
        "youtube_video_id": "dQw4w9WgXcQ",
        "youtube_start": None,
    },
    {
        "category_event_pk": 23,
        "category_name": "Seminaarit",
        "name": "Creative Coding with Shadertoy",
        "description": "Introduction to shader programming using Shadertoy. "
        "Learn the basics of GLSL and create your first visual effects.",
        "youtube_video_id": "u5HAYVHsasc",
        "youtube_start": 30,
    },
    {
        "category_event_pk": 23,
        "category_name": "Seminaarit",
        "name": "Chiptune Production Workshop",
        "description": "Learn how to create authentic chiptune music. "
        "Covers trackers, synthesis, and composition techniques.",
        "youtube_video_id": "vZa0Yh6e7dw",
        "youtube_start": None,
    },
    # Instanssi 2024 - Live-esitykset
    {
        "category_event_pk": 23,
        "category_name": "Live-esitykset",
        "name": "Opening Ceremony",
        "description": "The opening ceremony of Instanssi 2024. "
        "Welcome speech and introduction to the weekend program.",
        "youtube_video_id": "9bZkp7q19f0",
        "youtube_start": None,
    },
    {
        "category_event_pk": 23,
        "category_name": "Live-esitykset",
        "name": "Prize Ceremony",
        "description": "Award ceremony for all compo winners. " "Congratulations to all participants!",
        "youtube_video_id": "L_jWHffIx5E",
        "youtube_start": None,
    },
    # Instanssi 2024 - Haastattelut
    {
        "category_event_pk": 23,
        "category_name": "Haastattelut",
        "name": "Interview: Demo Compo Winner",
        "description": "Post-compo interview with the demo competition winner. "
        "Discussion about the creative process and technical challenges.",
        "youtube_video_id": "Zi_XLOBDo_Y",
        "youtube_start": None,
    },
    # Instanssi 2023 - Seminaarit
    {
        "category_event_pk": 22,
        "category_name": "Seminaarit",
        "name": "History of Finnish Demoscene",
        "description": "A deep dive into the history of Finnish demoscene groups. "
        "From the Amiga era to modern productions.",
        "youtube_video_id": "JGwWNGJdvx8",
        "youtube_start": None,
    },
    {
        "category_event_pk": 22,
        "category_name": "Seminaarit",
        "name": "Size Coding Techniques",
        "description": "Advanced techniques for 256 byte and 4K intro development. "
        "Compression, code golf, and optimization tricks.",
        "youtube_video_id": "y8OnoxKotPQ",
        "youtube_start": 120,
    },
    # Instanssi 2023 - Behind the Scenes
    {
        "category_event_pk": 22,
        "category_name": "Behind the Scenes",
        "name": "Organizing Instanssi",
        "description": "A look behind the curtain at what goes into organizing a demoparty. "
        "From venue booking to network setup.",
        "youtube_video_id": "kJQP7kiw5Fk",
        "youtube_start": None,
    },
    # Instanssi 2026 - Ennakkovideot (upcoming event)
    {
        "category_event_pk": 25,
        "category_name": "Ennakkovideot",
        "name": "Instanssi 2026 Teaser",
        "description": "Official teaser trailer for Instanssi 2026! "
        "Join us February 26-28 for an unforgettable weekend of demos, music, and creativity.",
        "youtube_video_id": "fJ9rUzIMcZQ",
        "youtube_start": None,
    },
    {
        "category_event_pk": 25,
        "category_name": "Ennakkovideot",
        "name": "Venue Tour 2026",
        "description": "Take a virtual tour of the Instanssi 2026 venue. "
        "See where the magic will happen!",
        "youtube_video_id": "2Vv-BfVoq4g",
        "youtube_start": 45,
    },
]

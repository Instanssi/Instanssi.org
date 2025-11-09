"""Test store items for the store"""

from datetime import UTC, datetime
from decimal import Decimal

# Store items for Instanssi 2026 (active event)
store_items_2026 = [
    {
        "event_pk": 25,  # Instanssi 2026
        "name": "Instanssi 2026 - Viikonloppulippu",
        "description": """Pääsylippu koko viikonlopun tapahtumaan!

Lippu sisältää:
- Pääsyn tapahtumaan koko viikonlopuksi (pe-su)
- Äänioikeuden kaikkiin kompoihin
- Mahdollisuuden osallistua kilpailuihin
- Pääsyn LAN-alueelle

Lippu toimitetaan sähköpostilla.""",
        "price": Decimal("25.00"),
        "max": 500,
        "available": True,
        "imagefile_type": "ticket",  # Use ticket image
        "max_per_order": 5,
        "sort_index": 1,
        "discount_amount": 5,  # Discount for 5+ tickets
        "discount_percentage": 10,  # 10% off
        "is_ticket": True,
        "is_secret": False,
        "secret_key": "",
    },
    {
        "event_pk": 25,
        "name": "Instanssi 2026 - Päivälippu lauantai",
        "description": """Päivälippu lauantaille.

Lippu sisältää:
- Pääsyn tapahtumaan lauantaina
- Äänioikeuden kaikkiin kompoihin
- Pääsyn LAN-alueelle

Lippu toimitetaan sähköpostilla.""",
        "price": Decimal("15.00"),
        "max": 200,
        "available": True,
        "imagefile_type": "ticket",  # Use ticket image
        "max_per_order": 5,
        "sort_index": 2,
        "discount_amount": -1,  # No discount
        "discount_percentage": 0,
        "is_ticket": True,
        "is_secret": False,
        "secret_key": "",
    },
    {
        "event_pk": 25,
        "name": "Instanssi 2026 T-paita",
        "description": """Virallinen Instanssi 2026 T-paita!

Korkealaatuinen puuvillapaita tapahtuman logolla.
Valitse koko lisätietoihin tilauksen yhteydessä.

Koot: S, M, L, XL, XXL

Paita noudetaan tapahtumasta infopisteeltä.""",
        "price": Decimal("20.00"),
        "max": 100,
        "available": True,
        "imagefile_type": "tshirt",  # Use t-shirt image
        "max_per_order": 3,
        "sort_index": 10,
        "discount_amount": -1,
        "discount_percentage": 0,
        "is_ticket": False,
        "is_secret": False,
        "secret_key": "",
    },
    {
        "event_pk": 25,
        "name": "Instanssi 2026 Tarra",
        "description": """Instanssi 2026 -tarra!

Kestävä vinyylitarra tapahtuman logolla.
Koko: noin 10x10cm

Tarra noudetaan tapahtumasta infopisteeltä.""",
        "price": Decimal("2.00"),
        "max": 300,
        "available": True,
        "imagefile_type": None,  # No image for stickers
        "max_per_order": 10,
        "sort_index": 11,
        "discount_amount": -1,
        "discount_percentage": 0,
        "is_ticket": False,
        "is_secret": False,
        "secret_key": "",
    },
    {
        "event_pk": 25,
        "name": "VIP-lippu (salainen)",
        "description": """VIP-pääsylippu erityiseduilla!

Sisältää:
- Kaikki normaalilipun edut
- Pääsy VIP-alueelle
- Ilmainen kahvi/tee
- Erityinen VIP-tarra

Saatavilla vain salaisella linkillä!""",
        "price": Decimal("50.00"),
        "max": 20,
        "available": True,
        "imagefile_type": "ticket",  # Use ticket image
        "max_per_order": 2,
        "sort_index": 0,
        "discount_amount": -1,
        "discount_percentage": 0,
        "is_ticket": True,
        "is_secret": True,
        "secret_key": "vip2026",
    },
]

# Store items for Instanssi 2024 (archived event)
store_items_2024 = [
    {
        "event_pk": 23,  # Instanssi 2024
        "name": "Instanssi 2024 - Viikonloppulippu",
        "description": "Pääsylippu koko viikonlopun tapahtumaan (LOPPUUNMYYTY)",
        "price": Decimal("22.00"),
        "max": 400,
        "available": False,  # Event is over
        "imagefile_type": "ticket",  # Use ticket image
        "max_per_order": 5,
        "sort_index": 1,
        "discount_amount": 5,
        "discount_percentage": 10,
        "is_ticket": True,
        "is_secret": False,
        "secret_key": "",
    },
    {
        "event_pk": 23,
        "name": "Instanssi 2024 T-paita",
        "description": "Virallinen Instanssi 2024 T-paita (LOPPUUNMYYTY)",
        "price": Decimal("18.00"),
        "max": 80,
        "available": False,
        "imagefile_type": "tshirt",  # Use t-shirt image
        "max_per_order": 3,
        "sort_index": 10,
        "discount_amount": -1,
        "discount_percentage": 0,
        "is_ticket": False,
        "is_secret": False,
        "secret_key": "",
    },
]

# Store items for Instanssi 2023
store_items_2023 = [
    {
        "event_pk": 22,  # Instanssi 2023
        "name": "Instanssi 2023 - Viikonloppulippu",
        "description": "Pääsylippu koko viikonlopun tapahtumaan (LOPPUUNMYYTY)",
        "price": Decimal("20.00"),
        "max": 350,
        "available": False,
        "imagefile_type": "ticket",  # Use ticket image
        "max_per_order": 5,
        "sort_index": 1,
        "discount_amount": -1,
        "discount_percentage": 0,
        "is_ticket": True,
        "is_secret": False,
        "secret_key": "",
    },
]

# Store item variants (sizes for t-shirts)
store_item_variants = [
    # Variants for 2026 T-shirt (index 2 in store_items_2026)
    {"item_event_pk": 25, "item_name": "Instanssi 2026 T-paita", "variant_name": "S"},
    {"item_event_pk": 25, "item_name": "Instanssi 2026 T-paita", "variant_name": "M"},
    {"item_event_pk": 25, "item_name": "Instanssi 2026 T-paita", "variant_name": "L"},
    {"item_event_pk": 25, "item_name": "Instanssi 2026 T-paita", "variant_name": "XL"},
    {"item_event_pk": 25, "item_name": "Instanssi 2026 T-paita", "variant_name": "XXL"},
    # Variants for 2024 T-shirt
    {"item_event_pk": 23, "item_name": "Instanssi 2024 T-paita", "variant_name": "S"},
    {"item_event_pk": 23, "item_name": "Instanssi 2024 T-paita", "variant_name": "M"},
    {"item_event_pk": 23, "item_name": "Instanssi 2024 T-paita", "variant_name": "L"},
    {"item_event_pk": 23, "item_name": "Instanssi 2024 T-paita", "variant_name": "XL"},
]

# All store items
store_items = store_items_2026 + store_items_2024 + store_items_2023

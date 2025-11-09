import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEST_IMAGE_1 = BASE_DIR / "files" / "image1.jpg"
TEST_IMAGE_2 = BASE_DIR / "files" / "image2.jpg"
TEST_IMAGE_3 = BASE_DIR / "files" / "image3.jpg"
TEST_VIDEO_1 = BASE_DIR / "files" / "video1.mp4"
TEST_ARCHIVE_1 = BASE_DIR / "files" / "archive1.zip"

TICKET1_IMAGE = BASE_DIR / "files" / "ticket1.png"
TICKET2_IMAGE = BASE_DIR / "files" / "ticket2.png"
T_SHIRT1_IMAGE = BASE_DIR / "files" / "tshirt1.png"
T_SHIRT2_IMAGE = BASE_DIR / "files" / "tshirt2.png"


def get_random_image_filename() -> Path:
    return random.choice([TEST_IMAGE_1, TEST_IMAGE_2, TEST_IMAGE_3])


def get_random_video_filename() -> Path:
    return random.choice([TEST_VIDEO_1])


def get_random_archive_filename() -> Path:
    return random.choice([TEST_ARCHIVE_1])


def get_random_ticket_product_image_filename() -> Path:
    return random.choice([TICKET1_IMAGE, TICKET2_IMAGE])


def get_random_tshirt_product_image_filename() -> Path:
    return random.choice([T_SHIRT1_IMAGE, T_SHIRT2_IMAGE])

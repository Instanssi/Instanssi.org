import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEST_IMAGE_1 = BASE_DIR / "files" / "image1.jpg"
TEST_IMAGE_2 = BASE_DIR / "files" / "image2.jpg"
TEST_IMAGE_3 = BASE_DIR / "files" / "image3.jpg"
TEST_VIDEO_1 = BASE_DIR / "files" / "video1.mp4"
TEST_ARCHIVE_1 = BASE_DIR / "files" / "archive1.zip"


def get_random_image_filename() -> Path:
    return random.choice([TEST_IMAGE_1, TEST_IMAGE_2, TEST_IMAGE_3])


def get_random_video_filename() -> Path:
    return random.choice([TEST_VIDEO_1])


def get_random_archive_filename() -> Path:
    return random.choice([TEST_ARCHIVE_1])

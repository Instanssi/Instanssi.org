from django.contrib.auth.models import AbstractUser
from django.db import models

LANGUAGE_CHOICES = [
    ("", "Not set"),
    ("en", "English"),
    ("fi", "Finnish"),
]


class User(AbstractUser):
    is_system = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="", blank=True)

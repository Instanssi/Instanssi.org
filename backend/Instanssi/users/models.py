from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = [
    ("", _("Not set")),
    ("en", _("English")),
    ("fi", _("Finnish")),
]


class User(AbstractUser):
    is_system = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="", blank=True)
    otherinfo = models.TextField(default="", blank=True)
    notify_vote_code_requests = models.BooleanField(default=True)
    notify_program_events = models.BooleanField(default=True)
    notify_compo_starts = models.BooleanField(default=True)
    notify_competition_starts = models.BooleanField(default=True)

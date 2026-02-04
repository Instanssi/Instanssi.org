from auditlog.registry import auditlog
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from Instanssi.common.html.fields import SanitizedHtmlField
from Instanssi.kompomaatti.models import Event


class BlogEntry(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("Event"), on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.SET_NULL, null=True)
    title = models.CharField(_("Title"), max_length=128)
    text = SanitizedHtmlField(_("Text"))
    date = models.DateTimeField(_("Date"), default=timezone.now)
    public = models.BooleanField(
        _("Public"),
        help_text=_("Public entries are shown on the event page and RSS feed."),
        default=False,
    )

    @classmethod
    def get_latest(cls, public: bool = True) -> QuerySet:
        return cls.objects.filter(public=public).order_by("-date")

    def __str__(self) -> str:
        return self.title


auditlog.register(BlogEntry)

from auditlog.registry import auditlog
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from Instanssi.kompomaatti.models import Event


class BlogEntry(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Käyttäjä", on_delete=models.SET_NULL, null=True)
    title = models.CharField("Otsikko", help_text="Lyhyt otsikko entrylle.", max_length=128)
    text = models.TextField("Teksti")
    date = models.DateTimeField("Aika", default=timezone.now)
    public = models.BooleanField(
        "Julkinen",
        help_text="Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.",
        default=False,
    )

    @classmethod
    def get_latest(cls, public: bool = True) -> QuerySet:
        return cls.objects.filter(public=public).order_by("-date")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entryt"


auditlog.register(BlogEntry)

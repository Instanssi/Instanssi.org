from django.contrib.auth.models import User
from django.db import models

from Instanssi.kompomaatti.models import Event


class DBLogEntry(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    module = models.CharField(max_length=64, blank=True)
    level = models.CharField(max_length=10)
    message = models.TextField()

    def __str__(self):
        if len(self.message) > 64:
            return "{} ...".format(self.message[:64])
        else:
            return self.message

    class Meta:
        verbose_name = "lokimerkintä"
        verbose_name_plural = "lokimerkinnät"

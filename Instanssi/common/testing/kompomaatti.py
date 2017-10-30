# -*- coding: utf-8 -*-

from django.utils import timezone
from Instanssi.kompomaatti.models import Event


class KompomaattiTestData(object):
    @staticmethod
    def create_test_event(name, **kwargs):
        event = Event()
        event.name = name
        event.date = kwargs.get('date', timezone.now())
        event.archived = kwargs.get('archived', False)
        event.mainurl = kwargs.get('mainurl', '')
        event.save()
        return event

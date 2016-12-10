# -*- coding: utf-8 -*-

from datetime import datetime

from django.test import TestCase
from Instanssi.store.models import StoreItem, StoreItemVariant
from Instanssi.kompomaatti.models import Event


class KompomaattiTests(TestCase):
    @staticmethod
    def create_test_event(name):
        event = Event()
        event.name = name
        event.date = datetime.now()
        return event.save()

    @staticmethod
    def create_test_item(name, event, **kwargs):
        item = StoreItem()
        item.name = name
        item.event = event

    def setUp(self):
        pass

# -*- coding: utf-8 -*-

import uuid
import logging
from decimal import Decimal
from random import randint

from Instanssi.common.misc import get_url
from Instanssi.store.models import TransactionItem
from Instanssi.store.utils.receipt import ReceiptParams
from Instanssi.store.models import Receipt
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.handlers import begin_payment_process, validate_item, TransactionException, validate_payment_method
from Instanssi.common.testing.store import StoreTestData, BitpayFakeResponse, PaytrailFakeResponse
from Instanssi.common.testing.kompomaatti import KompomaattiTestData
from Instanssi.common.testing.utils import q_reverse


from django.core.urlresolvers import reverse
from django.utils import timezone
import mock
from faker import Faker


from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.test import TestCase


class APIUnauthenticatedTests(TestCase):
    def setUp(self):
        self.api = APIClient()

    def tearDown(self):
        pass

    def test_events(self):
        url = '/api/v1/events/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_songs(self):
        url = '/api/v1/songs/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_competitions(self):
        url = '/api/v1/competitions/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_competition_participations(self):
        url = '/api/v1/competition_participations/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_user_participations(self):
        url = '/api/v1/user_participations/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_compos(self):
        url = '/api/v1/compos/'
        self.assertEqual(self.api.get(url).status_code, 200)

    def test_compo_entries(self):
        url = '/api/v1/compo_entries/'
        self.assertEqual(self.api.get(url).status_code, 200)

    def test_user_entries(self):
        url = '/api/v1/user_entries/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_programme_events(self):
        url = '/api/v1/programme_events/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_sponsors(self):
        url = '/api/v1/sponsors/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_messages(self):
        url = '/api/v1/messages/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_irc_message(self):
        url = '/api/v1/irc_messages/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.patch(url).status_code, 405)
        self.assertEqual(self.api.delete(url).status_code, 405)
        self.assertEqual(self.api.put(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_store_items(self):
        url = '/api/v1/store_items/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.patch(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.delete(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.put(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_store_transaction(self):
        url = '/api/v1/store_transaction/'
        self.assertEqual(self.api.get(url).status_code, 405)
        self.assertEqual(self.api.post(url).status_code, 400)  # No data = bad req. Tested properly in store tests.
        self.assertEqual(self.api.patch(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.delete(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.put(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_current_user(self):
        url = '/api/v1/current_user/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_user_vote_codes(self):
        url = '/api/v1/user_vote_codes/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_user_vote_code_requests(self):
        url = '/api/v1/user_vote_code_requests/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_user_votes(self):
        url = '/api/v1/user_votes/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.patch(url).status_code, 401)
        self.assertEqual(self.api.delete(url).status_code, 401)
        self.assertEqual(self.api.put(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)


class APIAuthenticatedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tony_tester', email='tony@instanssi.org', password='tester_password')
        self.api = APIClient()
        self.api.login(username='tony_tester', password='tester_password')

    def tearDown(self):
        self.api.logout()

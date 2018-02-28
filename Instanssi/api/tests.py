# -*- coding: utf-8 -*-

from datetime import timedelta
import base64

import mock
from faker import Faker
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from Instanssi.kompomaatti.models import Event, Compo, Competition, Entry
from Instanssi.store.models import TransactionItem, StoreTransaction, StoreItem


test_image = base64.decodebytes(
    b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeA'
    b'AAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcE'
    b'hZcwAADsMAAA7DAcdvqGQAAAAMSURBVBhXY2BgYAAAAAQ'
    b'AAVzN/2kAAAAASUVORK5CYII=')


class APIUnauthenticatedTests(TestCase):
    def setUp(self):
        self.api = APIClient()

    def tearDown(self):
        pass

    def test_events(self):
        url = '/api/v1/events/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_songs(self):
        url = '/api/v1/songs/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_competitions(self):
        url = '/api/v1/competitions/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_competition_participations(self):
        url = '/api/v1/competition_participations/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_user_participations(self):
        url = '/api/v1/user_participations/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_compos(self):
        url = '/api/v1/compos/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_compo_entries(self):
        url = '/api/v1/compo_entries/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_user_entries(self):
        url = '/api/v1/user_entries/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_programme_events(self):
        url = '/api/v1/programme_events/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_sponsors(self):
        url = '/api/v1/sponsors/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_messages(self):
        url = '/api/v1/messages/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_irc_message(self):
        url = '/api/v1/irc_messages/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_store_items(self):
        url = '/api/v1/store_items/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_store_transaction(self):
        url = '/api/v1/store_transaction/'
        self.assertEqual(self.api.get(url).status_code, 405)
        self.assertEqual(self.api.post(url).status_code, 400)  # No data = bad req. Tested properly in store tests.
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_current_user(self):
        url = '/api/v1/current_user/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_user_vote_codes(self):
        url = '/api/v1/user_vote_codes/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_user_vote_code_requests(self):
        url = '/api/v1/user_vote_code_requests/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)

    def test_user_votes(self):
        url = '/api/v1/user_votes/'
        self.assertEqual(self.api.get(url).status_code, 401)
        self.assertEqual(self.api.post(url).status_code, 401)
        self.assertEqual(self.api.options(url).status_code, 401)


class APIAuthenticatedTests(TestCase):
    def setUp(self):
        self.maxDiff = 8192
        self.user = User.objects.create_user(
            username='tony_tester', email='tony@instanssi.org', password='tester_password')
        self.user_b = User.objects.create_user(
            username='mary_tester', email='mary@instanssi.org', password='tester_password')
        self.event = Event.objects.create(
            name='Instanssi 3000',
            date=timezone.now(),
            archived=False,
            mainurl="http://localhost/"
        )
        self.compo = Compo.objects.create(
            event=self.event,
            name="Test Compo",
            description="Test Compo is the awesomest ever!",
            adding_end=timezone.now() + timedelta(hours=1),
            editing_end=timezone.now() + timedelta(hours=2),
            compo_start=timezone.now() + timedelta(hours=6),
            voting_start=timezone.now() + timedelta(hours=6, minutes=30),
            voting_end=timezone.now() + timedelta(hours=8)
        )
        self.compo_b = Compo.objects.create(
            event=self.event,
            name="Test Compo",
            description="Test Compo is the awesomest ever!",
            adding_end=timezone.now() + timedelta(hours=-6),
            editing_end=timezone.now() + timedelta(hours=-2),
            compo_start=timezone.now() + timedelta(hours=-1),
            voting_start=timezone.now() + timedelta(minutes=-30),
            voting_end=timezone.now() + timedelta(hours=8)
        )
        self.compo_entry = Entry.objects.create(
            compo=self.compo_b,
            user=self.user_b,
            name='Test Entry',
            description='Test Entry',
            creator='Test Creator',
            entryfile=SimpleUploadedFile("test_entry_file.zip", b'content', content_type="application/zip")
        )
        self.competition = Competition.objects.create(
            event=self.event,
            name="Test competition",
            description="Test competition is the awesomest ever!",
            participation_end=timezone.now() + timedelta(hours=1),
            start=timezone.now() + timedelta(hours=1, minutes=30),
            end=timezone.now() + timedelta(hours=8),
            score_type='p'
        )
        self.store_item = StoreItem.objects.create(
            event=self.event,
            name='Test Product',
            description='Test Product description',
            price=1.00,
            max=10,
            available=True,
            is_ticket=True
        )
        self.store_transaction = StoreTransaction.objects.create(
            token='1234',
            time_created=timezone.now(),
            time_paid=timezone.now(),
            key='461705a2a14e83676d7e227c0a16b51e00000000',
            firstname='Teija',
            lastname='Testaaja',
            email='teija.testaaja@nonexistent.inv',
            street='Kekkostie 19',
            postalcode='10000',
            city='Kekkonen'
        )
        self.store_transaction_item = TransactionItem.objects.create(
            key='461705a2a14e83676d7e227c0a16b51e67aec6f6',
            item=self.store_item,
            transaction=self.store_transaction,
            time_delivered=timezone.now(),
            purchase_price=1.00,
            original_price=1.00
        )
        self.store_transaction_item_b = TransactionItem.objects.create(
            key='461705a2a14e83676d7e227c0a16b51e67aec6f9',
            item=self.store_item,
            transaction=self.store_transaction,
            time_delivered=timezone.now(),
            purchase_price=1.00,
            original_price=1.00
        )

        self.api = APIClient()
        self.api.login(username='tony_tester', password='tester_password')

    def tearDown(self):
        self.api.logout()

    def test_events(self):
        url = '/api/v1/events/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_songs(self):
        """ Test songs api access without group, should return 403 for all """
        url = '/api/v1/songs/'
        self.assertEqual(self.api.get(url).status_code, 403)
        self.assertEqual(self.api.post(url).status_code, 403)
        self.assertEqual(self.api.options(url).status_code, 403)

    def test_competitions(self):
        url = '/api/v1/competitions/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_competition_participations(self):
        url = '/api/v1/competition_participations/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_user_participations(self):
        url = '/api/v1/user_participations/'

        # Test POST
        req = self.api.post(url, data={
            'competition': self.competition.id,
            'participant_name': 'Pertti Partisipantti',
        })
        self.assertEqual(req.status_code, 201)

        # Test POST: This should fail
        req = self.api.post(url, data={
            'competition': self.competition.id,
            'participant_name': 'Pertti Partisipantti 2',
        })
        self.assertEqual(req.status_code, 400)
        self.assertDictEqual(req.data, {'non_field_errors': ['Olet jo osallistunut tähän kilpailuun']})

        # Test GET: Make sure data looks okay
        req = self.api.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertListEqual(req.data, [{
            'id': 1,
            'competition': self.competition.id,
            'participant_name': 'Pertti Partisipantti',
        }])

        # Test OPTIONS for main page
        self.assertEqual(self.api.options(url).status_code, 200)

        instance_url = "{}{}/".format(url, 1)

        # Test out PATCH
        req = self.api.patch(instance_url, data={
            'id': 2,  # Should not change
            'participant_name': 'Pertti Perusjuntti',  # Should change
        })
        self.assertEqual(req.status_code, 200)

        # Make sure entry changed
        req = self.api.get(instance_url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            'id': 1,
            'competition': self.competition.id,
            'participant_name': 'Pertti Perusjuntti',
        })

        # Test PUT
        req = self.api.put(instance_url, data={
            'competition': self.competition.id,
            'participant_name': 'Pertti Partisipantti',
        })
        self.assertEqual(req.status_code, 200)

        # Make sure entry changed
        req = self.api.get(instance_url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            'id': 1,
            'competition': self.competition.id,
            'participant_name': 'Pertti Partisipantti',
        })

        # Test DELETE
        self.assertEqual(self.api.delete(instance_url).status_code, 204)

        # Make sure GET now says 404
        self.assertEqual(self.api.get(instance_url).status_code, 404)

        # Lastly, test out OPTIONS
        self.assertEqual(self.api.options(instance_url).status_code, 200)

    def test_compos(self):
        url = '/api/v1/compos/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_compo_entries(self):
        url = '/api/v1/compo_entries/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_user_entries(self):
        url = '/api/v1/user_entries/'

        # Test POST
        entry_file = SimpleUploadedFile("test_entry_file.zip", b'content', content_type="application/zip")
        source_file = SimpleUploadedFile("test_source_file.zip", b'content', content_type="application/zip")
        image_file = SimpleUploadedFile("image_file.png", test_image, content_type="image/png")
        req = self.api.post(url, format='multipart', data={
            'compo': self.compo.id,
            'name': 'Test Entry',
            'description': 'Awesome test entry description',
            'creator': 'Test Creator 2000',
            'entryfile': entry_file,
            'imagefile_original': image_file,
            'sourcefile': source_file
        })
        self.assertEqual(req.status_code, 201)

        # Test GET: Make sure data looks okay
        req = self.api.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertListEqual(req.data, [{
            'id': 2,
            'compo': self.compo.id,
            'name': 'Test Entry',
            'description': 'Awesome test entry description',
            'creator': 'Test Creator 2000',
            'entryfile_url': req.data[0]['entryfile_url'],
            'sourcefile_url': req.data[0]['sourcefile_url'],
            'imagefile_original_url': req.data[0]['imagefile_original_url'],
            'imagefile_thumbnail_url': req.data[0]['imagefile_thumbnail_url'],
            'imagefile_medium_url': req.data[0]['imagefile_medium_url'],
            'disqualified': False,
            'disqualified_reason': ''
        }])
        self.assertIsNotNone(req.data[0]['entryfile_url'])
        self.assertIsNotNone(req.data[0]['sourcefile_url'])
        self.assertIsNotNone(req.data[0]['imagefile_original_url'])
        self.assertIsNotNone(req.data[0]['imagefile_thumbnail_url'])
        self.assertIsNotNone(req.data[0]['imagefile_medium_url'])

        # Test main page OPTIONS
        self.assertEqual(self.api.options(url).status_code, 200)

        instance_url = "{}{}/".format(url, 2)

        # Test out PATCH
        req = self.api.patch(instance_url, format='multipart', data={
            'id': 3,  # Should not change
            'name': 'Test Entry 2',  # Should change
            'description': 'Awesome test entry description 2',  # Should change
            'creator': 'Test Creator 3000',  # Should change
            'imagefile_original': '',
        })
        self.assertEqual(req.status_code, 200)

        # Make sure entry changed
        req = self.api.get(instance_url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            'id': 2,
            'compo': self.compo.id,
            'name': 'Test Entry 2',
            'description': 'Awesome test entry description 2',
            'creator': 'Test Creator 3000',
            'entryfile_url': req.data['entryfile_url'],
            'sourcefile_url': req.data['sourcefile_url'],
            'imagefile_original_url': None,
            'imagefile_thumbnail_url': None,
            'imagefile_medium_url': None,
            'disqualified': False,
            'disqualified_reason': ''
        })
        self.assertIsNotNone(req.data['entryfile_url'])
        self.assertIsNotNone(req.data['sourcefile_url'])

        # Test out PUT
        entry_file = SimpleUploadedFile("test_entry_file.zip", b'content', content_type="application/zip")
        source_file = SimpleUploadedFile("test_source_file.zip", b'content', content_type="application/zip")
        image_file = SimpleUploadedFile("image_file.png", test_image, content_type="image/png")
        req = self.api.put(instance_url, format='multipart', data={
            'compo': self.compo.id,
            'name': 'Test Entry',
            'description': 'Awesome test entry description',
            'creator': 'Test Creator 2000',
            'entryfile': entry_file,
            'imagefile_original': image_file,
            'sourcefile': source_file
        })
        self.assertEqual(req.status_code, 200)

        # Make sure entry changed
        req = self.api.get(instance_url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            'id': 2,
            'compo': self.compo.id,
            'name': 'Test Entry',
            'description': 'Awesome test entry description',
            'creator': 'Test Creator 2000',
            'entryfile_url': req.data['entryfile_url'],
            'sourcefile_url': req.data['sourcefile_url'],
            'imagefile_original_url': req.data['imagefile_original_url'],
            'imagefile_thumbnail_url': req.data['imagefile_thumbnail_url'],
            'imagefile_medium_url': req.data['imagefile_medium_url'],
            'disqualified': False,
            'disqualified_reason': ''
        })
        self.assertIsNotNone(req.data['entryfile_url'])
        self.assertIsNotNone(req.data['sourcefile_url'])
        self.assertIsNotNone(req.data['imagefile_original_url'])
        self.assertIsNotNone(req.data['imagefile_thumbnail_url'])
        self.assertIsNotNone(req.data['imagefile_medium_url'])

        # Test DELETE
        self.assertEqual(self.api.delete(instance_url).status_code, 204)

        # Make sure GET now says 404
        self.assertEqual(self.api.get(instance_url).status_code, 404)

        # Lastly, test out OPTIONS
        self.assertEqual(self.api.options(instance_url).status_code, 200)

    def test_programme_events(self):
        url = '/api/v1/programme_events/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_sponsors(self):
        url = '/api/v1/sponsors/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_messages(self):
        url = '/api/v1/messages/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_irc_message(self):
        url = '/api/v1/irc_messages/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_store_items(self):
        url = '/api/v1/store_items/'
        self.assertEqual(self.api.get(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 403)  # Unauthorized by permission class
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_store_transaction(self):
        url = '/api/v1/store_transaction/'
        self.assertEqual(self.api.get(url).status_code, 405)
        self.assertEqual(self.api.post(url).status_code, 400)  # No data = bad req. Tested properly in store tests.
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_current_user(self):
        url = '/api/v1/current_user/'
        req = self.api.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            "id": self.user.id,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email
        })
        self.assertEqual(self.api.post(url).status_code, 405)
        self.assertEqual(self.api.options(url).status_code, 200)

    def test_user_vote_codes(self):
        url = '/api/v1/user_vote_codes/'

        # Test POST
        req = self.api.post(url, data={
            'event': self.event.id,
            'ticket_key': self.store_transaction_item.key
        })
        self.assertEqual(req.status_code, 201)

        # Test POST: This should fail
        req = self.api.post(url, data={
            'event': self.event.id,
            'ticket_key': self.store_transaction_item.key
        })
        self.assertEqual(req.status_code, 400)
        self.assertDictEqual(req.data, {'non_field_errors': ['Äänestyskoodi on jo hankittu']})

        # Test GET: Make sure data looks okay
        req = self.api.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertListEqual(req.data, [{
            'id': 1,
            'event': self.event.id,
            'time': req.data[0]['time'],
            'ticket_key': self.store_transaction_item.key
        }])

        # Test instance stuff. DELETE, PUT, PATCH = 405 (methods not implemented)
        instance_url = "{}{}/".format(url, 1)
        self.assertEqual(self.api.put(instance_url, data={}).status_code, 405)
        self.assertEqual(self.api.delete(instance_url).status_code, 405)
        self.assertEqual(self.api.patch(instance_url, data={}).status_code, 405)
        self.assertEqual(self.api.get(instance_url).status_code, 200)
        self.assertEqual(self.api.options(instance_url).status_code, 200)

    def test_user_vote_code_requests(self):
        url = '/api/v1/user_vote_code_requests/'

        # Test POST
        req = self.api.post(url, data={
            'event': self.event.id,
            'text': 'Test request',
        })
        self.assertEqual(req.status_code, 201)

        # Test POST: This should fail
        req = self.api.post(url, data={
            'event': self.event.id,
            'text': 'Test request',
        })
        self.assertEqual(req.status_code, 400)
        self.assertDictEqual(req.data, {'non_field_errors': ['Äänestyskoodipyyntö on jo olemassa']})

        # Test GET: Make sure data looks okay
        req = self.api.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertListEqual(req.data, [{
            'id': 1,
            'event': self.event.id,
            'text': 'Test request',
            'status': 0
        }])

        # Test main page OPTIONS
        self.assertEqual(self.api.options(url).status_code, 200)

        instance_url = "{}{}/".format(url, 1)

        # Test out PATCH
        self.assertEqual(self.api.patch(instance_url, data={
            'id': 2,  # Should not change
            'text': 'Test request 2',  # Should change
        }).status_code, 200)

        # Make sure entry changed
        req = self.api.get(instance_url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            'id': 1,
            'event': self.event.id,
            'text': 'Test request 2',
            'status': 0
        })

        # Test out PUT
        req = self.api.put(instance_url, data={
            'event': self.event.id,
            'text': 'Test request',
        })
        self.assertEqual(req.status_code, 200)

        # Make sure entry changed
        req = self.api.get(instance_url)
        self.assertEqual(req.status_code, 200)
        self.assertDictEqual(req.data, {
            'id': 1,
            'event': self.event.id,
            'text': 'Test request',
            'status': 0
        })

        # Test DELETE (should error out)
        self.assertEqual(self.api.delete(instance_url).status_code, 405)

        # Lastly, test out OPTIONS
        self.assertEqual(self.api.options(instance_url).status_code, 200)

    def test_user_votes(self):
        url = '/api/v1/user_votes/'

        # Test POST: This should fail due to compo voting not started
        req = self.api.post(url, data={
            'compo': self.compo.id,
            'entries': [self.compo_entry.id]
        })
        self.assertEqual(req.status_code, 400)
        self.assertDictEqual(req.data, {'non_field_errors': ['Kompon äänestysaika ei ole voimassa']})

        # Test POST: this should fail due to missing vote rights
        req = self.api.post(url, data={
            'compo': self.compo_b.id,
            'entries': [self.compo_entry.id]
        })
        self.assertEqual(req.status_code, 400)
        self.assertDictEqual(req.data, {'non_field_errors': ['Äänestysoikeus puuttuu']})

        # Test POST: Get voting rights
        req = self.api.post('/api/v1/user_vote_codes/', data={
            'event': self.event.id,
            'ticket_key': self.store_transaction_item_b.key
        })
        self.assertEqual(req.status_code, 201)

        # Test POST: This should succeed
        req = self.api.post(url, data={
            'compo': self.compo_b.id,
            'entries': [self.compo_entry.id]
        })
        self.assertEqual(req.status_code, 201)

        # Test POST: This should also succeed
        req = self.api.post(url, data={
            'compo': self.compo_b.id,
            'entries': [self.compo_entry.id]
        })
        self.assertEqual(req.status_code, 201)

        # Test GET: Make sure data looks okay
        req = self.api.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertListEqual(req.data, [{
            'compo': self.compo_b.id,
            'entries': [self.compo_entry.id]
        }])

        # Test instance stuff. DELETE, PUT, PATCH = 405 (methods not implemented)
        instance_url = "{}{}/".format(url, 1)
        self.assertEqual(self.api.put(instance_url, data={}).status_code, 405)
        self.assertEqual(self.api.delete(instance_url).status_code, 405)
        self.assertEqual(self.api.patch(instance_url, data={}).status_code, 405)
        self.assertEqual(self.api.get(instance_url).status_code, 200)
        self.assertEqual(self.api.options(instance_url).status_code, 200)

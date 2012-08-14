# -*- coding: utf-8 -*-

from django.utils import unittest
from django.contrib.auth.models import User, Permission
from django.test.client import Client
from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
from Instanssi.kompomaatti.models import Event
from datetime import datetime

class AdminArkistoUserTestCase(unittest.TestCase):
    def setUp(self):
        # Tuples: Username/password, and boolean value that tells whether we expect to be permitted or not.
        self.users = [('admin', True), ('grouped', True), ('normal', False), ('anon', False)]
        
        # Creae admin user
        self.user_admin = User.objects.create_superuser('admin', 'admin@users.com', 'admin')
        self.user_admin.is_staff = True
        self.user_admin.is_superuser = True
        self.user_admin.save()
        
        # Create grouped staff user
        self.user_grouped = User.objects.create_user('grouped', 'grouped@users.com', 'grouped')
        self.user_grouped.is_staff = True
        self.user_grouped.save()
        perms = [           
            'add_othervideo',
            'change_othervideo',
            'delete_othervideo',
            'add_othervideocategory', 
            'change_othervideocategory',
            'delete_othervideocategory',
        ]
        for perm in perms: 
            self.user_grouped.user_permissions.add(Permission.objects.get(codename=perm))
        self.user_grouped.save()
        
        # Create normal staff user
        self.user_normal = User.objects.create_user('normal', 'normal@users.com', 'normal')
        self.user_normal.is_staff = True
        self.user_normal.save()
        
        # Create non-staff user
        self.user_anon = User.objects.create_user('anon', 'anon@users.com', 'anon')
        
        # Create test event
        self.test_event = Event(name="TestEvent", date=datetime.now())
        self.test_event.save()
        
        # Create category for each user, and add some test data to each category
        self.test_cats = {}
        self.test_vids = {}
        for user_info in self.users:
            user = user_info[0]
            
            # Create data
            vids = []
            cats = []
            for i in range(2):
                cat = OtherVideoCategory(event=self.test_event, name=user+"_cat_"+str(i))
                cat.save()
                cats.append(cat)
                vid = OtherVideo(category=cat, name=user+"_vid_"+str(i), description="TestDescription", youtube_url="http://www.youtube.com/v/1234234")
                vid.save()
                vids.append(vid)
            
            # Add to dictionaries
            self.test_cats[user] = cats
            self.test_vids[user] = vids
        
    def test_arkisto(self):
        # Test permissions for users
        for user_info in self.users:
            user = user_info[0]
            expect = user_info[1]
            
            # Attempt to log in, and make sure it succeeded
            c = Client()
            log = c.login(username=user, password=user)
            self.assertEqual(log, True, u'Unable to log in as '+user+'!')
            
            # List of tuples with page address, and expected value if everything works.
            pages = {
                ('/control/arkisto/addvid/', 200),
                ('/control/arkisto/editvid/'+str(self.test_vids[user][0].id)+'/', 200),
                ('/control/arkisto/deletevid/'+str(self.test_vids[user][1].id)+'/', 302),
                ('/control/arkisto/addvidcat/', 200),
                ('/control/arkisto/editcat/'+str(self.test_cats[user][0].id)+'/', 200),
                ('/control/arkisto/deletecat/'+str(self.test_cats[user][1].id)+'/', 302),
            }
            
            # Test pages
            for page_info in pages:
                # Get tuple values
                page = page_info[0]
                expect_code = page_info[1]
                
                # If we expect to fail, return value will be 404
                if not expect:
                    expect_code = 404
                
                # Test
                r = c.get(page)
                self.assertEqual(r.status_code, expect_code, u'Error while testing '+page+' as user '+user+'. Got code '+str(r.status_code)+', but expected '+str(expect_code)+'.')
            


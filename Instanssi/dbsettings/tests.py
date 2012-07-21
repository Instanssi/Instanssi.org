from django.utils import unittest
from Instanssi.dbsettings.models import Setting

class SettingTestCase(unittest.TestCase):
    def setUp(self):
        Setting.set(u"lion", u"roar")
        Setting.set(u"cat_in_tree", True)
        Setting.set(u"cat_not_in_tree", False)
        Setting.set(u"count_cats", 123423)
        Setting.set(u"Gentoo", u"vroom!")
        Setting.set(u"Gentoo", u"vroom, vroom!")
        Setting.set(u"GroupedItem1", u'String', u'AwesomeGroup')
        Setting.set(u"GroupedItem2", 234234, u'AwesomeGroup')
        self.testd = {
            'GroupedItem1': u"String",
            'GroupedItem2': 234234,
        }
        
    def test_fetch(self):
        self.assertEqual(Setting.get(u"lion"), u"roar", u"Detected problem with saving strings!")
        self.assertEqual(Setting.get(u"cat_in_tree"), True, u"Detected problem with saving booleans!")
        self.assertEqual(Setting.get(u"cat_not_in_tree"), False, u"Detected problem with saving booleans!")
        self.assertEqual(Setting.get(u"count_cats"), 123423, u"Detected problem with saving integers!")
        self.assertEqual(Setting.get(u"Gentoo"), u"vroom, vroom!", u"Detected problem with overwriting an existing settings key!")
        self.assertDictEqual(Setting.get_by_group(u'AwesomeGroup'), self.testd, u"Detected problem with getting settings by groupname!")

    
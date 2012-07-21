# -*- coding: utf-8 -*-

from django.db import models

class Setting(models.Model):
    key = models.CharField(u'Avain', help_text=u'Asetuksen avain', max_length=32)
    group = models.CharField(u'Ryhmä', help_text=u'Ryhmän nimi', max_length=32)
    value = models.CharField(u'Arvo', help_text=u'Asetuksen arvo', max_length=128)
    SETTING_TYPES = (
        (0, u'Integer'),
        (1, u'Boolean'), 
        (2, u'String'),
    )
    type = models.IntegerField(u'Tyyppi', help_text=u'Asetuksen tyyppi (Boolean=1, Integer=0, String=2).', choices=SETTING_TYPES)
    
    def __unicode__(self):
        return self.key
    
    class Meta:
        verbose_name=u"asetus"
        verbose_name_plural=u"asetukset"
        unique_together = ("key", "group")

    @staticmethod
    def get(key, group=u''):
        p = Setting.objects.get(key=key, group=group)
        if p.type == 0:
            return int(p.value)
        elif p.type == 1:
            if p.value == u"0":
                return False
            else:
                return True
        else:
            return unicode(p.value)
        
    @staticmethod
    def get_by_group(group):
        return Setting.objects.filter(group=group)
    
    @staticmethod
    def set(key, value, group=u''):
        # Guess type
        if type(value) == str or type(value) == unicode:
            t = 2
        elif type(value) == int or type(value) == long:
            t = 0
            value = str(value)
        elif type(value) == bool:
            t = 1
            if value:
                value = u"1"
            else:
                value = u"0"
        else:
            raise TypeError(u"Can not set a variable of given type!")
        
        # Get old if it exists, otherwise create new setting
        try:
            setting = Setting.objects.get(key=key, group=group)
        except:
            setting = Setting()
            setting.key = key
            setting.group = group
        
        # Set type and value, then save.
        setting.type = t
        setting.value = value
        setting.save()
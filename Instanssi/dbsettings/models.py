from django.db import models

class Setting(models.Model):
    key = models.CharField(u'Avain', help_text=u'Asetuksen avain', max_length=32)
    value = models.CharField(u'Arvo', help_text=u'Asetuksen arvo', max_length=128)
    SETTING_TYPES = (
        (0, u'Integer'),
        (1, u'Boolean'), 
        (2, u'String'),
    )
    type = models.IntegerField(u'Tyyppi', help_text=u'Asetuksen tyyppi (Boolean, Integer, String).', choices=SETTING_TYPES)
    
    def __unicode__(self):
        return self.key
    
    class Meta:
        verbose_name=u"asetus"
        verbose_name_plural=u"asetukset"

    @staticmethod
    def get(key):
        p = Setting.objects.get(key=key)
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
    def set(key, value, t=-1):
        # If type is not given, try to guess
        if t == -1:
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
            setting = Setting.objects.get(key=key)
        except:
            setting = Setting()
            setting.key = key
        
        # Set type and value, then save.
        setting.type = t
        setting.value = value
        setting.save()
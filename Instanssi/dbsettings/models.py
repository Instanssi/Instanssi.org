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
        
    def get(self, key):
        return self.objects.get(key=key)
    
    def set(self, key, value, type):
        try:
            setting = self.objects.get(key=key)
        except:
            setting = Setting()
            setting.key = key
            setting.type = type
        setting.value = value
        setting.save()
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Compo(models.Model):
    name = models.CharField('Name', max_length=32)
    description = models.TextField('Description')
    add_deadline = models.DateTimeField('Deadline for uploads')
    edit_deadline = models.DateTimeField('Deadline for edits')
    time = models.DateTimeField('Compo time')
    def __unicode__(self):
        return self.name
    
class Entry(models.Model):
    user = models.ForeignKey(User)
    compo = models.ForeignKey(Compo)
    name = models.CharField('Name', max_length=64)
    description = models.TextField('Description')
    creator = models.CharField('Creator name', max_length=64)
    file = models.FileField(upload_to='entries/')
    def __unicode__(self):
        return self.name

class Vote(models.Model):
    user = models.ForeignKey(User)
    compo = models.ForeignKey(Compo)
    entry = models.ForeignKey(Entry)
    def __unicode__(self):
        return self.entry.name + ' by ' + self.user.name
    
admin.site.register(Compo)
admin.site.register(Entry)
admin.site.register(Vote)
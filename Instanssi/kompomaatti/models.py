from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Compo(models.Model):
    name = models.CharField('Name', max_length=32)
    description = models.TextField('Description')
    adding_end = models.DateTimeField('Deadline for uploads')
    editing_end = models.DateTimeField('Deadline for edits')
    compo_start = models.DateTimeField('Compo time')
    voting_start = models.DateTimeField('Voting opens')
    voting_end = models.DateTimeField('Voting ends')
    sizelimit = models.IntegerField('File size limit')
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
        return self.name + ' by ' + self.creator + ' (uploaded by ' + self.user.username + ')'

class Vote(models.Model):
    user = models.ForeignKey(User)
    compo = models.ForeignKey(Compo)
    entry = models.ForeignKey(Entry)
    rank = models.IntegerField('Rank')
    def __unicode__(self):
        return self.entry.name + ' by ' + self.user.username + ' as ' + self.rank
    
admin.site.register(Compo)
admin.site.register(Entry)
admin.site.register(Vote)
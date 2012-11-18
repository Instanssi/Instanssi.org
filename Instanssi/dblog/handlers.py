# -*- coding: utf-8 -*-

from logging import Handler
from datetime import datetime 

class DBLogHandler(Handler, object):
    def __init__(self):
        super(DBLogHandler, self).__init__()
    
    def emit(self, record):
        from models import DBLogEntry as _LogEntry
        
        entry = _LogEntry()
        entry.level = record.levelname
        entry.message = self.format(record)
        entry.module = record.name
        try:
            entry.event = record.event
        except:
            try:
                entry.event_id = record.event_id
            except:
                pass
        try:
            entry.user = record.user
        except:
            pass
        entry.save()


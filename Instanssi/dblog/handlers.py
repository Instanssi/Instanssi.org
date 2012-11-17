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
        if record.event:
            entry.event = record.event
        if record.user:
            entry.user = record.user
        entry.save()


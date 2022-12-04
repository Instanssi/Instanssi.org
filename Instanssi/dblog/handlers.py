from logging import Handler, LogRecord


class DBLogHandler(Handler, object):
    def __init__(self):
        super(DBLogHandler, self).__init__()

    def emit(self, record: LogRecord) -> None:
        from .models import DBLogEntry as _LogEntry

        entry = _LogEntry()
        entry.level = record.levelname
        entry.message = self.format(record)
        entry.module = record.name
        entry.event = getattr(record, "event", None)
        entry.event_id = getattr(record, "event_id", None)
        entry.user = getattr(record, "user", None)
        entry.save()

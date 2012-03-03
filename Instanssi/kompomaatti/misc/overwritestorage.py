# -*- coding: utf-8 -*-

from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        newname = super(FileSystemStorage, self).get_available_name(name)
        if self.exists(name):
            self.delete(name)
        return newname
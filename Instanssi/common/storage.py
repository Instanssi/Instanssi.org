# -*- coding: utf-8 -*-

import unicodedata
from django.core.files.storage import FileSystemStorage


class ASCIIFileSystemStorage(FileSystemStorage):
    def get_valid_name(self, name):
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
        return super(ASCIIFileSystemStorage, self).get_valid_name(name)

# -*- coding: utf-8 -*-

from Instanssi import settings
from django.http import Http404

if settings.ACTIVE_EVENT_ID == -1:
    raise Http404
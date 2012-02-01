# -*- coding: utf-8 -*-

from Instanssi.kompomaatti.misc.custom_render import custom_render

def help(request):
    return custom_render(request, 'kompomaatti/help.html')
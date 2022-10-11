# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2023/'+templatename+'.html', {
        'event_id': 22,  # Instanssi 2023 ID
        'templatename': templatename,
    })

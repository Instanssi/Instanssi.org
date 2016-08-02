# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2015/'+templatename+'.html', {
        'event_id': 12,
        'templatename': templatename,
    })

# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2016/'+templatename+'.html', {
        'event_id': 14,
        'templatename': templatename,
    })

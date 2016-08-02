# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2017/'+templatename+'.html', {
        'event_id': 15,
        'templatename': templatename,
    })

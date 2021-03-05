# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2018/'+templatename+'.html', {
        'event_id': 16,
        'templatename': templatename,
    })

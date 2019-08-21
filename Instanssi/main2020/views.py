# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2020/'+templatename+'.html', {
        'event_id': 18,
        'templatename': templatename,
    })

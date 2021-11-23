# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2022/'+templatename+'.html', {
        'event_id': 20,
        'templatename': templatename,
    })

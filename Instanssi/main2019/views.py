# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2019/'+templatename+'.html', {
        'event_id': 17,
        'templatename': templatename,
    })

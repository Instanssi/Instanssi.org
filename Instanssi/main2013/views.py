# -*- coding: utf-8 -*-

from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2013/'+templatename+'.html', {
        'event_id': 5, 
        'templatename': templatename,
    })

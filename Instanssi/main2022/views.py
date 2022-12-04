from django.shortcuts import render


def pageloader(request, templatename):
    return render(request, 'main2022/'+templatename+'.html', {
        'event_id': 21,  # Instanssi goes revision ID
        'templatename': templatename,
    })

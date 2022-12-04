from django.shortcuts import render


def admin_render(request, tpl, context=None):
    if not context:
        context = {}
    return render(request, tpl, context)

from django.http import Http404


def dummy_index(request, *args, **kwargs):
    raise Http404()

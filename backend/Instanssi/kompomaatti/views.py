from django.http import Http404


def dummy_index(request, *args, **kwargs):
    """
    This just returns 404. Normally we would see new kompomaatti UI due to nginx redirect, so this is here
    only so that we can retain the natural redirects from urls.py.
    """
    raise Http404()

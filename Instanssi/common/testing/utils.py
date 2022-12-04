from django.urls import reverse
from django.utils.http import urlencode


def q_reverse(view_name, query=None, **kwargs):
    url = reverse(view_name, kwargs=kwargs)
    if query:
        return "{}?{}".format(url, urlencode(query))
    return url

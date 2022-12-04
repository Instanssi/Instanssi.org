import hashlib
from django import template

register = template.Library()


@register.simple_tag
def gravatar_url(email):
    return 'https://www.gravatar.com/avatar/{}?d=retro'.format(hashlib.md5(email.lower().encode('UTF-8')).hexdigest())

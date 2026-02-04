import hashlib

from django import template

register = template.Library()


@register.simple_tag
def gravatar_url(email: str) -> str:
    return (
        f"https://www.gravatar.com/avatar/{hashlib.md5(email.lower().encode('UTF-8')).hexdigest()}?d=retro"
    )

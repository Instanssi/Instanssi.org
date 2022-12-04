from datetime import datetime, timedelta

import arrow
from django.conf import settings


def format_single_helper(k: datetime):
    test = arrow.get(k)
    now = arrow.utcnow()
    today = arrow.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    t_plus_one = today + timedelta(days=1)
    t_plus_two = today + timedelta(days=2)
    t_plus_three = today + timedelta(days=3)

    if test < now:
        return "päättynyt"
    elif now < test < t_plus_one:
        return "tänään klo. " + test.to(settings.TIME_ZONE).format("HH:mm", locale="fi_FI")
    elif t_plus_one < test < t_plus_two:
        return "huomenna klo. " + test.to(settings.TIME_ZONE).format("HH:mm", locale="fi_FI")
    elif t_plus_two < test < t_plus_three:
        return "ylihuomenna klo. " + test.to(settings.TIME_ZONE).format("HH:mm", locale="fi_FI")
    else:
        return test.to(settings.TIME_ZONE).format("DD.MM.YYYY klo. HH:mm", locale="fi_FI")


def format_single(t):
    return format_single_helper(t).capitalize()


def format_between(tp1, tp2):
    t1 = arrow.get(tp1)
    t2 = arrow.get(tp2)
    now = arrow.utcnow()
    today = arrow.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    if t2 < now:
        return "Päättynyt"
    elif t1 < now < t2:
        left = t2 - now
        l_hours = int(left.total_seconds() / timedelta(hours=1).total_seconds())
        l_minutes = int((left.total_seconds() - timedelta(hours=l_hours).total_seconds()) / 60)
        if l_hours == 0:
            return "Menossa, aikaa jäljellä {} minuuttia".format(l_minutes)
        else:
            return "Menossa, aikaa jäljellä {} tuntia ja {} minuuttia".format(l_hours, l_minutes)

    elif now < t1 < (today + timedelta(days=3)):
        return "Alkaa {} ja päättyy {}.".format(format_single_helper(t1), format_single_helper(t2))
    else:
        return "Alkaa {} ja päättyy {}.".format(
            t1.to(settings.TIME_ZONE).format("DD.MM.YYYY klo. HH:mm", locale="fi_FI"),
            t2.to(settings.TIME_ZONE).format("DD.MM.YYYY klo. HH:mm", locale="fi_FI"),
        )

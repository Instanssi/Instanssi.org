# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.utils import timezone


def todayhelper():
    today = timezone.now().date()
    return datetime(day=today.day, year=today.year, month=today.month, tzinfo=timezone.now().tzinfo)


def format_single_helper(t):
    now = timezone.now()
    today = todayhelper()
    tomorrow = today + timedelta(days=1)
    the_day_after_tomorrow = today + timedelta(days=2)  # Must honor the movie!
    
    if t < now:
        return "päättynyt"
    elif now < t < tomorrow:
        return "tänään klo. " + t.strftime("%H:%M")
    elif tomorrow < t < the_day_after_tomorrow:
        return "huomenna klo. " + t.strftime("%H:%M")
    elif the_day_after_tomorrow < t < today + timedelta(days=3):
        return "ylihuomenna klo. " + t.strftime("%H:%M")
    else:
        return t.strftime("%d.%m.%Y klo. %H:%M")


def format_single(t):
    return format_single_helper(t).capitalize()


# Since python 2.6 does not support deltatime.total_seconds() ... :<
def delta_total_seconds(delta):
    return delta.days * 86400 + delta.seconds


def format_between(t1, t2):
    now = timezone.now()
    today = todayhelper()

    if t2 < now:
        return "Päättynyt"
    elif t1 < now < t2:
        left = t2-now
        l_hours = int(delta_total_seconds(left) / delta_total_seconds(timedelta(hours=1)))
        l_minutes = int((delta_total_seconds(left) - delta_total_seconds(timedelta(hours=l_hours))) / 60)
        if l_hours == 0:
            return "Menossa, aikaa jäljellä {} minuuttia".format(l_minutes)
        else:
            return "Menossa, aikaa jäljellä {} tuntia ja {} minuuttia".format(l_hours, l_minutes)

    elif now < t1 < today + timedelta(days=3):
        return "Alkaa {} ja päättyy {}.".format(format_single_helper(t1), format_single_helper(t2))
    else:
        return "Alkaa {} ja päättyy {}.".format(t1.strftime("%d.%m.%Y %H:%M"), t2.strftime("%d.%m.%Y %H:%M"))

# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

def todayhelper():
    today = datetime.today()
    return datetime(day=today.day, year=today.year, month=today.month)

def format_single_helper(t):
    now = datetime.now()
    today = todayhelper()
    tomorrow = today + timedelta(days=1)
    the_day_after_tomorrow = today + timedelta(days=2) # Must honor the movie!
    
    if t < now:
        return "päättynyt"
    elif t >= now and t < tomorrow:
        return "tänään klo. " + t.strftime("%H:%M")
    elif t >= tomorrow and t < the_day_after_tomorrow:
        return "huomenna klo. " + t.strftime("%H:%M")
    elif t >= the_day_after_tomorrow and t < today+timedelta(days=3):
        return "ylihuomenna klo. " + t.strftime("%H:%M")
    else:
        return t.strftime("%d.%m.%Y klo. %H:%M")

def format_single(t):
    return format_single_helper(t).capitalize()

def format_between(t1, t2):
    now = datetime.now()
    today = todayhelper()
    tomorrow = today + timedelta(days=1)
    the_day_after_tomorrow = today + timedelta(days=2) # Must honor the movie!
    
    if t2 < now:
        return "Päättynyt"
    elif t1 < now and t2 > now:
        left = t2-now
        l_hours = int(left.total_seconds() / timedelta(hours=1).total_seconds())
        l_minutes = int((left.total_seconds() - timedelta(hours=l_hours).total_seconds()) / 60)
        if(l_hours == 0):
            return "Menossa, aikaa jäljellä " + str(l_minutes) + " minuuttia"
        else:
            return "Menossa, aikaa jäljellä " + str(l_hours) + " tuntia ja " + str(l_minutes) + " minuuttia"
    elif t1 > now and t1 < today+timedelta(days=3):
        return "Alkaa " + format_single_helper(t1) + " ja päättyy " + format_single_helper(t2)
    else:
        return "Alkaa " + t1.strftime("%d.%m.%Y %H:%M") + " ja päättyy " + t2.strftime("%d.%m.%Y %H:%M") + "."
    
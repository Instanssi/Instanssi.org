# -*- coding: utf-8 -*-

def sizeformat(size):
    kb = 1024
    mb = kb*1024
    gb = mb*1024
    if size > gb:
        return str(round(size/gb, 2)) + ' Gt'
    if size > mb:
        return str(round(size/mb, 2)) + ' Mt'
    if size > kb:
        return str(round(size/kb, 2)) + ' Kt'
    return str(size) + ' t'
    
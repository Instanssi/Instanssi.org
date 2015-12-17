# -*- coding: utf-8 -*-


def sizeformat(size):
    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    if size > gb:
        return u'{} Gt'.format(round(size/gb, 2))
    if size > mb:
        return u'{} Mt'.format(round(size/mb, 2))
    if size > kb:
        return u'{} Kt'.format(round(size/kb, 2))
    return u'{} t'.format(size)

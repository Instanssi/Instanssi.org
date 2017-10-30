# -*- coding: utf-8 -*-


def sort_by_score(entries):
    return sorted(entries, key=lambda o: o.get_score(), reverse=True)

# -*- coding: utf-8 -*-


# Helper function for sorting by entry score
def helper(object):
    return object.get_score()


# Sorts entries by score
def sort_by_score(entries):
    return sorted(entries, key=helper, reverse=True)
# -*- coding: utf-8 -*-

from . import awesometime


def compo_times_formatter(compo):
    compo.compo_time = awesometime.format_single(compo.compo_start)
    compo.adding_time = awesometime.format_single(compo.adding_end)
    compo.editing_time = awesometime.format_single(compo.editing_end)
    compo.voting_time = awesometime.format_between(compo.voting_start, compo.voting_end)
    return compo


def competition_times_formatter(competition):
    competition.start_time = awesometime.format_single(competition.start)
    competition.participation_end_time = awesometime.format_single(competition.participation_end)
    return competition

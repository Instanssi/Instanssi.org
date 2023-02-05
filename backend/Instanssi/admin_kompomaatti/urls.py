from django.urls import path

from Instanssi.admin_kompomaatti.views import (
    accept_vote_code_request,
    competition_delete,
    competition_edit,
    competition_participation_edit,
    competition_participations,
    competition_score,
    competitions_browse,
    compo_browse,
    compo_delete,
    compo_edit,
    entries_csv,
    entry_browse,
    entry_delete,
    entry_edit,
    generate_result_package,
    index,
    reject_vote_code_request,
    results,
    ticket_vote_codes,
    vote_code_requests,
)

app_name = "admin_kompomaatti"


urlpatterns = [
    path("", index, name="index"),
    path("compos/", compo_browse, name="compos"),
    path("editcompo/<int:compo_id>/", compo_edit, name="compo-edit"),
    path("deletecompo/<int:compo_id>/", compo_delete, name="compo-delete"),
    path("entries_csv/", entries_csv, name="entries_csv"),
    path("entries/", entry_browse, name="entries"),
    path("editentry/<int:entry_id>/", entry_edit, name="entry-edit"),
    path("deleteentry/<int:entry_id>/", entry_delete, name="entry-delete"),
    path("competitions/", competitions_browse, name="competitions"),
    path("editcompetition/<int:competition_id>/", competition_edit, name="competition-edit"),
    path("deletecompetition/<int:competition_id>/", competition_delete, name="competition-delete"),
    path("score/<int:competition_id>/", competition_score, name="score"),
    path("participations/<int:competition_id>/", competition_participations, name="participations"),
    path(
        "participations_edit/<int:competition_id>/edit/<int:participation_id>/",
        competition_participation_edit,
        name="participation-edit",
    ),
    path("results/", results, name="results"),
    path("generate_result_package/<int:compo_id>/", generate_result_package, name="generate_result_package"),
    path("ticket_votecodes/", ticket_vote_codes, name="ticket_votecodes"),
    path("votecoderequests/", vote_code_requests, name="votecoderequests"),
    path("acceptreq/<int:vote_code_request_id>/", accept_vote_code_request, name="votecoderequest-accept"),
    path("rejectreq/<int:vote_code_request_id>/", reject_vote_code_request, name="votecoderequest-reject"),
]

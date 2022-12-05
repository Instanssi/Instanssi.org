from django.conf.urls import url

from Instanssi.admin_arkisto.views import (
    archiver,
    delete_video,
    delete_video_category,
    edit_video,
    edit_video_category,
    hide,
    index,
    optimizes_scores,
    remove_old_votes,
    show,
    transfer_rights,
    video_categories,
    videos,
)

app_name = "admin_arkisto"


urlpatterns = [
    url("", index, name="index"),
    url("archiver/", archiver, name="archiver"),
    url("show/", show, name="archiver-show"),
    url("hide/", hide, name="archiver-hide"),
    url("transferrights/", transfer_rights, name="archiver-tr"),
    url("optimizescores/", optimizes_scores, name="archiver-os"),
    url("removeoldvotes/", remove_old_votes, name="archiver-rv"),
    url("vids/", videos, name="vids"),
    url("vidcats/", video_categories, name="vidcats"),
    url("deletevid/<int:video_id>/", delete_video, name="vids-delete"),
    url("deletecat/<int:category_id>/", delete_video_category, name="vidcats-delete"),
    url("editvid/<int:video_id>/", edit_video, name="vids-edit"),
    url("editcat/<int:category_id>/", edit_video_category, name="vidcats-edit"),
]

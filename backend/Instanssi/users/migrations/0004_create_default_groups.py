from typing import Any

from django.db import migrations
from django.db.models import Q

GROUP_PERMISSIONS: dict[str, list[tuple[str, str]]] = {
    "staff_defaults": [
        ("admin_upload", "add_uploadedfile"),
        ("admin_upload", "change_uploadedfile"),
        ("admin_upload", "delete_uploadedfile"),
        ("admin_upload", "view_uploadedfile"),
        ("arkisto", "add_othervideo"),
        ("arkisto", "add_othervideocategory"),
        ("arkisto", "change_othervideo"),
        ("arkisto", "change_othervideocategory"),
        ("arkisto", "delete_othervideo"),
        ("arkisto", "delete_othervideocategory"),
        ("arkisto", "view_othervideo"),
        ("arkisto", "view_othervideocategory"),
        ("auth", "view_group"),
        ("auth", "view_permission"),
        ("ext_blog", "add_blogentry"),
        ("ext_blog", "change_blogentry"),
        ("ext_blog", "delete_blogentry"),
        ("ext_blog", "view_blogentry"),
        ("ext_programme", "add_programmeevent"),
        ("ext_programme", "change_programmeevent"),
        ("ext_programme", "delete_programmeevent"),
        ("ext_programme", "view_programmeevent"),
        ("kompomaatti", "add_alternateentryfile"),
        ("kompomaatti", "add_competition"),
        ("kompomaatti", "add_competitionparticipation"),
        ("kompomaatti", "add_compo"),
        ("kompomaatti", "add_entry"),
        ("kompomaatti", "add_event"),
        ("kompomaatti", "add_profile"),
        ("kompomaatti", "add_ticketvotecode"),
        ("kompomaatti", "add_vote"),
        ("kompomaatti", "add_votecoderequest"),
        ("kompomaatti", "add_votegroup"),
        ("kompomaatti", "change_alternateentryfile"),
        ("kompomaatti", "change_competition"),
        ("kompomaatti", "change_competitionparticipation"),
        ("kompomaatti", "change_compo"),
        ("kompomaatti", "change_entry"),
        ("kompomaatti", "change_event"),
        ("kompomaatti", "change_profile"),
        ("kompomaatti", "change_ticketvotecode"),
        ("kompomaatti", "change_vote"),
        ("kompomaatti", "change_votecoderequest"),
        ("kompomaatti", "change_votegroup"),
        ("kompomaatti", "view_alternateentryfile"),
        ("kompomaatti", "view_competition"),
        ("kompomaatti", "view_competitionparticipation"),
        ("kompomaatti", "view_compo"),
        ("kompomaatti", "view_entry"),
        ("kompomaatti", "view_event"),
        ("kompomaatti", "view_profile"),
        ("kompomaatti", "view_ticketvotecode"),
        ("kompomaatti", "view_vote"),
        ("kompomaatti", "view_votecoderequest"),
        ("kompomaatti", "view_votegroup"),
        ("store", "view_storeitem"),
        ("store", "view_storeitemvariant"),
        ("users", "view_user"),
    ],
    "store": [
        ("store", "add_receipt"),
        ("store", "add_storeitem"),
        ("store", "add_storeitemvariant"),
        ("store", "add_storetransaction"),
        ("store", "add_storetransactionevent"),
        ("store", "add_transactionitem"),
        ("store", "change_receipt"),
        ("store", "change_storeitem"),
        ("store", "change_storeitemvariant"),
        ("store", "change_storetransaction"),
        ("store", "change_storetransactionevent"),
        ("store", "change_transactionitem"),
        ("store", "delete_receipt"),
        ("store", "delete_storeitem"),
        ("store", "delete_storeitemvariant"),
        ("store", "delete_storetransaction"),
        ("store", "delete_storetransactionevent"),
        ("store", "delete_transactionitem"),
        ("store", "view_receipt"),
        ("store", "view_storeitem"),
        ("store", "view_storeitemvariant"),
        ("store", "view_storetransaction"),
        ("store", "view_storetransactionevent"),
        ("store", "view_transactionitem"),
    ],
    "tokens": [
        ("knox", "add_authtoken"),
        ("knox", "change_authtoken"),
        ("knox", "delete_authtoken"),
        ("knox", "view_authtoken"),
    ],
}


def forwards(apps: Any, schema_editor: Any) -> None:
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for group_name, perms in GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        if perms:
            q = Q()
            for app_label, codename in perms:
                q |= Q(content_type__app_label=app_label, codename=codename)
            group.permissions.set(Permission.objects.filter(q))


def backwards(apps: Any, schema_editor: Any) -> None:
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUP_PERMISSIONS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_user_is_system"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

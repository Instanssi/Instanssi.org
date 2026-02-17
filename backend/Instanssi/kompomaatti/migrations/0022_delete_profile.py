from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("kompomaatti", "0021_add_sorting_indexes"),
        ("users", "0008_user_otherinfo"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Profile",
        ),
    ]

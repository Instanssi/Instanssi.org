from django.db import models


class InfodeskAccess(models.Model):
    """Permission holder for infodesk access control.

    This model has no database table; it exists solely to provide
    Django permissions that can be assigned to infodesk staff.
    """

    class Meta:
        managed = False
        default_permissions = ("view", "change")

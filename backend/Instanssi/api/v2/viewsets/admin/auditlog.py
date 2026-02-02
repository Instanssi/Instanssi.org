from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter

from Instanssi.api.v2.serializers.admin.auditlog_serializer import LogEntrySerializer
from Instanssi.api.v2.utils.base import PermissionReadOnlyViewSet


class LogEntryFilter(filters.FilterSet):  # type: ignore[misc]
    """Filter for audit log entries."""

    app_label = filters.CharFilter(method="filter_by_content_type")
    model = filters.CharFilter(method="filter_by_content_type")
    object_pk = filters.CharFilter(field_name="object_pk")

    class Meta:
        model = LogEntry
        fields = ["app_label", "model", "object_pk"]

    def filter_by_content_type(
        self, queryset: QuerySet[LogEntry], _name: str, _value: str
    ) -> QuerySet[LogEntry]:
        """Filter by app_label and model combined."""
        app_label = self.data.get("app_label")
        model = self.data.get("model")

        if app_label and model:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                return queryset.filter(content_type=content_type)
            except ContentType.DoesNotExist:
                return queryset.none()
        return queryset


class AuditLogViewSet(PermissionReadOnlyViewSet):
    """Read-only viewset for viewing audit log entries.

    Requires auditlog.view_logentry permission. Model-specific filtering
    is handled in get_queryset().
    """

    serializer_class = LogEntrySerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    filterset_class = LogEntryFilter
    ordering = ["-timestamp"]
    ordering_fields = ["timestamp"]

    def get_queryset(self) -> QuerySet[LogEntry]:
        """Return audit log entries filtered by user's model permissions."""
        queryset: QuerySet[LogEntry] = LogEntry.objects.select_related("content_type", "actor")
        user = self.request.user

        # If user is superuser, return all entries
        if user.is_superuser:
            return queryset

        # Filter to only include entries for models the user can view
        allowed_content_types: list[int] = []
        for ct in ContentType.objects.all():
            perm = f"{ct.app_label}.view_{ct.model}"
            if user.has_perm(perm):
                allowed_content_types.append(ct.pk)

        return queryset.filter(content_type_id__in=allowed_content_types)

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter

from Instanssi.api.v2.serializers.admin.auditlog_serializer import LogEntrySerializer
from Instanssi.api.v2.utils.base import PermissionReadOnlyViewSet


class LogEntryFilter(filters.FilterSet):
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
    ordering = ("-timestamp",)
    ordering_fields = ["timestamp"]

    def get_queryset(self) -> QuerySet[LogEntry]:
        """Return audit log entries filtered by user's model permissions."""
        queryset: QuerySet[LogEntry] = LogEntry.objects.select_related("content_type", "actor")
        user = self.request.user

        # If user is superuser, return all entries
        if user.is_superuser:
            return queryset

        # Get all user permissions at once (more efficient than checking each ContentType)
        user_perms = user.get_all_permissions()

        # Extract app_label.model pairs from view_* permissions
        viewable_models: set[tuple[str, str]] = set()
        for perm in user_perms:
            if ".view_" in perm:
                # Permission format: "app_label.view_modelname"
                app_label, perm_name = perm.split(".", 1)
                model_name = perm_name.removeprefix("view_")
                viewable_models.add((app_label, model_name))

        if not viewable_models:
            return queryset.none()

        # Get ContentType IDs for allowed models in a single query
        q_filter = Q()
        for app_label, model in viewable_models:
            q_filter |= Q(app_label=app_label, model=model)

        allowed_ct_ids = list(ContentType.objects.filter(q_filter).values_list("pk", flat=True))

        return queryset.filter(content_type_id__in=allowed_ct_ids)

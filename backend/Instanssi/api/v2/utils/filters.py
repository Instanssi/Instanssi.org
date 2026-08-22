from django import forms
from django.db import models
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field


@extend_schema_field(OpenApiTypes.INT)
class IntegerFilter(filters.NumberFilter):
    field_class = forms.IntegerField


class BaseFilterSet(filters.FilterSet):
    FILTER_DEFAULTS = {
        **filters.FilterSet.FILTER_DEFAULTS,
        models.ForeignKey: {"filter_class": IntegerFilter},
        models.OneToOneField: {"filter_class": IntegerFilter},
    }


class ApiFilterBackend(filters.DjangoFilterBackend):
    filterset_base = BaseFilterSet

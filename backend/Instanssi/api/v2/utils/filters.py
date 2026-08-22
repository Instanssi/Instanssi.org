from django import forms
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field


@extend_schema_field(OpenApiTypes.INT)
class IntegerFilter(filters.NumberFilter):
    field_class = forms.IntegerField

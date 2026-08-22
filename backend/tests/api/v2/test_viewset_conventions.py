"""Conventions enforced for every APIv2 viewset.

These tests walk the /api/v2/ URL tree so that new endpoints are covered
automatically:

- Any django-filter backend must be ApiFilterBackend, so foreign key filters
  accept plain integer ids and return an empty list for unknown ids instead of
  a validation error (which would allow probing which ids exist).
- Any hand-written FilterSet must inherit BaseFilterSet for the same reason.
- Every paginated list endpoint must have a deterministic default ordering,
  otherwise LimitOffsetPagination can duplicate or skip rows across pages.
"""

from django.urls import URLPattern, URLResolver, get_resolver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView

from Instanssi.api.v2.utils.filters import ApiFilterBackend, BaseFilterSet


def _iter_view_classes(resolver, prefix=""):
    for pattern in resolver.url_patterns:
        path = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            yield from _iter_view_classes(pattern, path)
        elif isinstance(pattern, URLPattern):
            cls = getattr(pattern.callback, "cls", None)
            if cls is not None:
                yield path, pattern.callback, cls


def _v2_list_views():
    """Yield (url, viewset class) for every APIv2 endpoint with a list action."""
    seen = set()
    for path, callback, cls in _iter_view_classes(get_resolver()):
        if "api/v2/" not in path or cls in seen:
            continue
        actions = getattr(callback, "actions", None) or {}
        if "list" not in actions.values():
            continue
        seen.add(cls)
        yield path, cls


def test_v2_viewsets_use_api_filter_backend():
    """FK filters must not 400 on unknown ids: only ApiFilterBackend is allowed."""
    offenders = []
    for path, cls in _v2_list_views():
        for backend in getattr(cls, "filter_backends", ()):
            if issubclass(backend, DjangoFilterBackend) and not issubclass(backend, ApiFilterBackend):
                offenders.append(f"{cls.__name__} ({path}) uses {backend.__name__}")
        filterset_class = getattr(cls, "filterset_class", None)
        if filterset_class is not None and not issubclass(filterset_class, BaseFilterSet):
            offenders.append(f"{cls.__name__} ({path}) filterset {filterset_class.__name__}")
    assert not offenders, "Use ApiFilterBackend/BaseFilterSet in:\n" + "\n".join(offenders)


def test_v2_paginated_viewsets_have_default_ordering():
    """Paginated lists need OrderingFilter and a non-empty default ordering."""
    offenders = []
    for path, cls in _v2_list_views():
        if not issubclass(cls, GenericAPIView) or cls.pagination_class is None:
            continue
        backends = getattr(cls, "filter_backends", ())
        has_ordering_filter = any(issubclass(b, OrderingFilter) for b in backends)
        if not has_ordering_filter or not getattr(cls, "ordering", None):
            offenders.append(f"{cls.__name__} ({path})")
    assert not offenders, "Paginated viewsets missing OrderingFilter or a default `ordering`:\n" + "\n".join(
        offenders
    )

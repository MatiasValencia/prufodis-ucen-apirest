from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.filters import SearchFilter


def has_view_permission(request, view):
    try:
        view.check_permissions(request)
    except (NotAuthenticated, PermissionDenied):
        return False

    return True


class PermissionAwareDjangoFilterBackend(DjangoFilterBackend):
    def to_html(self, request, queryset, view):
        if not has_view_permission(request, view):
            return ""

        return super().to_html(request, queryset, view)


class PermissionAwareSearchFilter(SearchFilter):
    def to_html(self, request, queryset, view):
        if not has_view_permission(request, view):
            return ""

        return super().to_html(request, queryset, view)

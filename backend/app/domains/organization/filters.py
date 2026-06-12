from fastapi_ronin import filters

from app.domains.organization.models import Organization, OrganizationUser


class OrganizationFilterSet(filters.FilterSet):
    fields = [
        filters.CharFilter('name', default_lookup='icontains'),
    ]

    class Meta:
        model = Organization


class OrganizationUserFilterSet(filters.FilterSet):
    fields = [
        filters.UUIDFilter('organization_id'),
    ]

    class Meta:
        model = OrganizationUser

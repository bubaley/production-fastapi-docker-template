from fastapi_ronin import filters

from app.domains.user.models import UserToken


class UserTokenFilterSet(filters.FilterSet):
    fields = [
        filters.UUIDFilter('user_id'),
    ]

    class Meta:
        model = UserToken

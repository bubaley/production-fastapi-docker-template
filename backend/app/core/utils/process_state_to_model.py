from fastapi import HTTPException
from fastapi_ronin.state import BaseStateManager

from app.core.auth import AuthState
from app.core.models import BaseModel
from app.shared.services.owned_data_provider import NOT_FOUND_MSG_ORGANIZATION


def _set_field_from_state(instance: BaseModel, state: AuthState, field_name: str, error_detail: str):
    field = instance._meta.fields_map.get(field_name)
    if field:
        state_value = getattr(state, field_name, None)
        if not state_value and not field.null:
            raise HTTPException(status_code=400, detail=error_detail)
        setattr(instance, field_name, state_value)


# use data for set fields if provided
def process_state_to_model(instance: BaseModel):
    # data = await OwnedDataProvider.process_request_headers(request, user)
    field_configs = [
        ('organization', NOT_FOUND_MSG_ORGANIZATION),
    ]
    state: AuthState = BaseStateManager.get_state().get('auth_state') or AuthState()

    for field_name, error_detail in field_configs:
        _set_field_from_state(instance, state, field_name, error_detail)
    return instance

from utils.logging import logging
from utils.constants import REDIRECT_URI
from pytest_nhsd_apim.auth_journey import (
    get_access_token_via_user_restricted_flow_combined_auth,
)


@logging(teaser="Getting OAuth token")
def get_oauth_token(base_url: str, app_key: str, app_secret: str) -> str:
    token = get_access_token_via_user_restricted_flow_combined_auth(
        identity_service_base_url=f"{base_url}/oauth2",
        client_id=app_key,
        client_secret=app_secret,
        callback_url=REDIRECT_URI,
        auth_scope="nhs-login",
        login_form={},
    )
    return token["access_token"]

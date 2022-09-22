from pytest_nhsd_apim.auth_journey import get_access_token_via_user_restricted_flow_combined_auth, \
    get_access_token_via_signed_jwt_flow

from tests.feature_tests.utils.constants import REDIRECT_URI
from tests.feature_tests.utils.logging import logging


@logging(teaser="Getting OAuth token")
def get_oauth_user_restricted_token(base_url: str, app_key: str, app_secret: str) -> str:
    token = get_access_token_via_user_restricted_flow_combined_auth(
        identity_service_base_url=f"{base_url}/oauth2",
        client_id=app_key,
        client_secret=app_secret,
        callback_url=REDIRECT_URI,
        auth_scope="nhs-login",
        login_form={},
    )
    return token["access_token"]


@logging(teaser="Getting OAuth token")
def get_oauth_app_restricted_token(base_url: str, app_key: str, jwt_key_pair) -> str:
    token = get_access_token_via_signed_jwt_flow(
        identity_service_base_url=f"{base_url}/oauth2",
        client_id=app_key,
        jwt_private_key=jwt_key_pair["private_key_pem"],
        jwt_kid="kid-1"
    )
    return token["access_token"]


def get_oauth_token(base_url: str, app_key: str, app_secret: str, jwt_key_pair, app_restricted: bool) -> str:
    if app_restricted:
        return get_oauth_app_restricted_token(
            base_url=base_url,
            app_key=app_key,
            jwt_key_pair=jwt_key_pair
        )

    return get_oauth_user_restricted_token(
        base_url=base_url,
        app_key=app_key,
        app_secret=app_secret
    )

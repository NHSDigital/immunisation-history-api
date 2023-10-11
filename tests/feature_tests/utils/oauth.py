import os
from time import time
from uuid import uuid4

import jwt
from pytest_nhsd_apim.auth_journey import get_access_token_via_signed_jwt_flow

from tests.feature_tests.utils.logging import logging


def _get_nhs_login_private_key() -> str:
    nhs_login_id_token_private_key_path = os.environ.get(
        "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH"
    )
    with open(nhs_login_id_token_private_key_path, "r") as f:
        return f.read()


def get_nhs_login_id_token(nhs_number: str, proofing_level: str):
    expires = int(time())
    payload = {
        "aud": 'tf_-APIM-1',
        "id_status": 'verified',
        "token_use": 'id',
        "auth_time": 1616600683,
        "iss": "https://internal-dev.api.service.nhs.uk",
        "sub": "https://internal-dev.api.service.nhs.uk",
        "exp": expires + 300,
        "iat": expires - 10,
        "vtm": 'https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk',
        "jti": str(uuid4()),
        "identity_proofing_level": proofing_level,
        "birthdate": "1939-09-26",
        "nhs_number": nhs_number,
        "nonce": "randomnonce",
        "surname": "CARTHY",
        "vot": f"{proofing_level}.Cp.Cd",
        "family_name": "CARTHY"
    }
    additional_headers = {
        "kid": "nhs-login",
        "typ": "JWT",
        "alg": "RS512"
    }

    jwt_private_key = _get_nhs_login_private_key()

    return jwt.encode(
        payload, jwt_private_key, algorithm="RS512", headers=additional_headers
    )


# This method from pytest-nhsd-apim has changed in later versions of the library so will need updating if these tests
# are required, however given the PR for this https://github.com/NHSDigital/immunisation-history-api/pull/157/files
# states that they did not run at the time of the commit, it is not being updated with the library update.
@logging(teaser="Getting OAuth token")
def get_oauth_token(base_url: str, app_key: str, app_jwt_private_key: str, id_token: str = None) -> str:
    token = get_access_token_via_signed_jwt_flow(
        identity_service_base_url=f"{base_url}/oauth2",
        client_id=app_key,
        jwt_private_key=app_jwt_private_key,
        jwt_kid="kid-1",
        id_token=id_token
    )
    return token["access_token"]

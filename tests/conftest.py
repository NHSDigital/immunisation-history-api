# flake8: noqa
import asyncio
from time import time
from uuid import uuid4

import pytest
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils.fixtures import api_client   # pylint: disable=unused-import
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.oauth_helper import OauthHelper
from .configuration.environment import ENV


@pytest.fixture(scope='session')
def api_test_config() -> APITestSessionConfig:
    return APITestSessionConfig()


@pytest.yield_fixture(scope='session')
def test_app():
    """Setup & Teardown an app-restricted app for this api"""
    app = ApigeeApiDeveloperApps()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        app.setup_app(
            api_products=[ENV["product"]],
            custom_attributes={
                'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/identity-service-jwks/main/jwks/internal-dev/9baed6f4-1361-4a8e-8531-1f8426e3aba8.json'  # noqa
            }
        )
    )
    app.oauth = OauthHelper(app.client_id, app.client_secret, "")
    yield app
    loop.run_until_complete(app.destroy_app())


async def get_token(
        app: ApigeeApiDeveloperApps, grant_type: str = "authorization_code", **kwargs
):
    oauth = app.oauth

    resp = await oauth.get_token_response(grant_type=grant_type, **kwargs)

    if resp['status_code'] != 200:
        message = 'unable to get token'
        raise RuntimeError(
            f"\n{'*' * len(message)}\n"
            f"MESSAGE: {message}\n"
            f"URL: {resp.get('url')}\n"
            f"STATUS CODE: {resp.get('status_code')}\n"
            f"RESPONSE: {resp.get('body')}\n"
            f"HEADERS: {resp.get('headers')}\n"
            f"{'*' * len(message)}\n"
        )
    return resp['body']


@pytest.fixture(scope="session")
def valid_access_token(test_app) -> str:

    jwt = test_app.oauth.create_jwt(
        **{
            "kid": "test-1",
            "claims": {
                "sub": test_app.client_id,
                "iss": test_app.client_id,
                "jti": str(uuid4()),
                "aud": ENV["token_url"],
                "exp": int(time()) + 60,
            },
        }
    )
    loop = asyncio.new_event_loop()
    token = loop.run_until_complete(get_token(test_app, grant_type="client_credentials", _jwt=jwt))
    return token["access_token"]


@pytest.fixture(scope="session")
def nhs_login_id_token(test_app, id_token_claims=None, id_token_headers=None) -> str:

    if not id_token_claims:
        id_token_claims = {
            'aud': 'tf_-APIM-1',
            'id_status': 'verified',
            'token_use': 'id',
            'auth_time': 1616600683,
            'iss': 'https://auth.sandpit.signin.nhs.uk',
            'vot': 'P9.Cp.Cd',
            'exp': int(time()) + 600,
            'iat': int(time()) - 10,
            'vtm': 'https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk',
            'jti': 'b68ddb28-e440-443d-8725-dfe0da330118'
        }
    if not id_token_headers:
        id_token_headers = {
            "sub": "49f470a1-cc52-49b7-beba-0f9cec937c46",
            "aud": "APIM-1",
            "kid": "nhs-login",
            "iss": "https://auth.sandpit.signin.nhs.uk",
            "typ": "JWT",
            "exp": 1616604574,
            "iat": 1616600974,
            "alg": "RS512",
            "jti": "b68ddb28-e440-443d-8725-dfe0da330118"
        }

    with open(ENV["nhs_login_id_token_private_key_path"], "r") as f:
        contents = f.read()

    id_token_jwt = test_app.oauth.create_id_token_jwt(algorithm='RS512',
                                                      claims=id_token_claims,
                                                      headers=id_token_headers,
                                                      signing_key=contents)

    return id_token_jwt

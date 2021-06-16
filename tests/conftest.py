# flake8: noqa
import asyncio
from time import time
from uuid import uuid4
import os

import pytest
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils.fixtures import api_client  # pylint: disable=unused-import
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from api_test_utils.oauth_helper import OauthHelper


def get_env(variable_name: str) -> str:
    """Returns a environment variable"""
    try:
        var = os.environ[variable_name]
        if not var:
            raise RuntimeError(f"Variable is null, Check {variable_name}.")
        return var
    except KeyError:
        raise RuntimeError(f"Variable is not set, Check {variable_name}.")


@pytest.fixture(scope="session")
def api_test_config() -> APITestSessionConfig:
    return APITestSessionConfig()


@pytest.yield_fixture(scope="session")
def test_app():
    """Setup & Teardown an app-restricted app for this api"""
    app = ApigeeApiDeveloperApps()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        app.setup_app(
            api_products=[get_env("APIGEE_PRODUCT")],
            custom_attributes={
                "jwks-resource-url": "https://raw.githubusercontent.com/NHSDigital/identity-service-jwks/main/jwks/internal-dev/9baed6f4-1361-4a8e-8531-1f8426e3aba8.json"  # noqa
            },
        )
    )
    app.oauth = OauthHelper(app.client_id, app.client_secret, app.callback_url)
    yield app
    loop.run_until_complete(app.destroy_app())


@pytest.yield_fixture()
def test_product_and_app():
    """Setup & Teardown an product and app for this api"""
    product = ApigeeApiProducts()
    app = ApigeeApiDeveloperApps()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(product.create_new_product())
    loop.run_until_complete(product.update_scopes(
        [
            "urn:nhsd:apim:app:level3:immunisation-history",
            "urn:nhsd:apim:user-nhs-login:P9:immunisation-history",
            "urn:nhsd:apim:user-nhs-login:P5:immunisation-history"
        ]
    ))
    loop.run_until_complete(
        app.setup_app(
            api_products=[product.name],
            custom_attributes={
                "jwks-resource-url": "https://raw.githubusercontent.com/NHSDigital/identity-service-jwks/main/jwks/internal-dev/9baed6f4-1361-4a8e-8531-1f8426e3aba8.json"  # noqa
            },
        )
    )
    app.oauth = OauthHelper(app.client_id, app.client_secret, app.callback_url)
    yield product, app
    loop.run_until_complete(app.destroy_app())
    loop.run_until_complete(product.destroy_product())


@pytest.yield_fixture(scope="session")
def test_product():
    """Setup & Teardown an product for this api"""
    product = ApigeeApiProducts()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(product.create_new_product())
    yield product
    loop.run_until_complete(product.destroy_product())


async def get_token(
    app: ApigeeApiDeveloperApps, grant_type: str = "authorization_code", **kwargs
):
    oauth = app.oauth

    resp = await oauth.get_token_response(grant_type=grant_type, **kwargs)

    if resp["status_code"] != 200:
        message = "unable to get token"
        raise RuntimeError(
            f"\n{'*' * len(message)}\n"
            f"MESSAGE: {message}\n"
            f"URL: {resp.get('url')}\n"
            f"STATUS CODE: {resp.get('status_code')}\n"
            f"RESPONSE: {resp.get('body')}\n"
            f"HEADERS: {resp.get('headers')}\n"
            f"{'*' * len(message)}\n"
        )
    return resp["body"]


@pytest.fixture(scope="session")
def valid_access_token(test_app) -> str:
    oauth_proxy = get_env("OAUTH_PROXY")
    oauth_base_uri = get_env("OAUTH_BASE_URI")
    token_url = f"{oauth_base_uri}/{oauth_proxy}/token"

    jwt = test_app.oauth.create_jwt(
        **{
            "kid": "test-1",
            "claims": {
                "sub": test_app.client_id,
                "iss": test_app.client_id,
                "jti": str(uuid4()),
                "aud": token_url,
                "exp": int(time()) + 60,
            },
        }
    )
    loop = asyncio.new_event_loop()
    token = loop.run_until_complete(
        get_token(test_app, grant_type="client_credentials", _jwt=jwt)
    )
    return token["access_token"]


def nhs_login_id_token(
    test_app: ApigeeApiDeveloperApps,
    id_token_claims: dict = None,
    id_token_headers: dict = None,
    allowed_proofing_level: str = 'P9'
) -> str:

    default_id_token_claims = {
        "aud": "tf_-APIM-1",
        "id_status": "verified",
        "token_use": "id",
        "auth_time": 1616600683,
        "iss": "https://internal-dev.api.service.nhs.uk",  # Points to internal dev -> testing JWKS
        "sub": "https://internal-dev.api.service.nhs.uk",
        "exp": int(time()) + 300,
        "iat": int(time()) - 10,
        "vtm": "https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk",
        "jti": str(uuid4()),
        "identity_proofing_level": allowed_proofing_level,
        "birthdate": "1939-09-26",
        "nhs_number": "9912003888",
        "nonce": "randomnonce",
        "surname": "CARTHY",
        "vot": "P9.Cp.Cd",
        "family_name": "CARTHY",
    }

    if id_token_claims is not None:
        default_id_token_claims = {**default_id_token_claims, **id_token_claims}

    default_id_token_headers = {
        "kid": "nhs-login",
        "typ": "JWT",
        "alg": "RS512"
    }

    if id_token_headers is not None:
        default_id_token_headers = {**default_id_token_headers, **id_token_headers}

    nhs_login_id_token_private_key_path = get_env("ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH")

    with open(nhs_login_id_token_private_key_path, "r") as f:
        contents = f.read()

    id_token_jwt = test_app.oauth.create_id_token_jwt(
        algorithm="RS512",
        claims=default_id_token_claims,
        headers=default_id_token_headers,
        signing_key=contents,
    )

    return id_token_jwt


async def get_token_nhs_login_token_exchange(test_app: ApigeeApiDeveloperApps,
                                             subject_token_claims: dict = None,
                                             client_assertion_jwt: dict = None):
    """Call identity server to get an access token"""
    if client_assertion_jwt is not None:
        client_assertion_jwt = test_app.oauth.create_jwt(kid="test-1",
                                                         claims=client_assertion_jwt)
    else:
        client_assertion_jwt = test_app.oauth.create_jwt(kid="test-1")

    if subject_token_claims is not None:
        id_token_jwt = nhs_login_id_token(
            test_app=test_app, id_token_claims=subject_token_claims
        )
    else:
        id_token_jwt = nhs_login_id_token(test_app=test_app)

    # When
    token_resp = await test_app.oauth.get_token_response(
        grant_type="token_exchange",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "subject_token": id_token_jwt,
            "client_assertion": client_assertion_jwt,
        },
    )
    assert token_resp["status_code"] == 200
    assert list(token_resp["body"].keys()) == ["access_token", "expires_in", "token_type", "issued_token_type"]
    return token_resp["body"]

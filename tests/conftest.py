# flake8: noqa
import json
import os
from typing import List, Dict
from uuid import uuid4
from time import time

import jwt
import pytest
import requests

from pytest_nhsd_apim.apigee_apis import (
    ApigeeClient,
    ApigeeNonProdCredentials,
    ApiProductsAPI,
    DeveloperAppsAPI,
)

from pytest_nhsd_apim.identity_service import (
    ClientCredentialsConfig,
    ClientCredentialsAuthenticator,
    TokenExchangeConfig,
    TokenExchangeAuthenticator
)

APP_EMAIL = "apm-testing-internal-dev@nhs.net"
ID_TOKEN_ISSUER = "https://identity.ptl.api.platform.nhs.uk/realms/NHS-Login-mock-internal-dev"


def get_env(variable_name: str, default: str = None) -> str:
    """Returns a environment variable"""
    try:
        var = os.environ.get(variable_name, default)
        if not var:
            raise RuntimeError(f"Variable is null, Check {variable_name}.")
        return var
    except KeyError:
        raise RuntimeError(f"Variable is not set, Check {variable_name}.")


def get_product_names(suffixes) -> List[str]:
    return [f'{get_env("APIGEE_PRODUCT")}{suffix}' for suffix in suffixes]


def get_oath_url(environment: str) -> str:
    default_base_oauth_url = f"https://{environment}.api.service.nhs.uk"
    return f'{get_env("OAUTH_BASE_URI", default=default_base_oauth_url)}/{get_env("OAUTH_PROXY", default="oauth2-mock")}'


def _get_nhs_login_private_key() -> str:
    nhs_login_id_token_private_key_path = os.environ.get(
        "ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH"
    )
    with open(nhs_login_id_token_private_key_path, "r") as f:
        return f.read()


def nhs_login_id_token(
    id_token_claims: Dict = None,
    id_token_headers: Dict = None,
    allowed_proofing_level: str = "P9",
) -> str:
    expires = int(time())
    default_id_token_claims = {
        "aud": "tf_-APIM-1",
        "id_status": "verified",
        "token_use": "id",
        "auth_time": 1616600683,
        "iss": ID_TOKEN_ISSUER,
        "sub": ID_TOKEN_ISSUER,
        "exp": expires + 300,
        "iat": expires - 10,
        "vtm": "https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk",
        "jti": str(uuid4()),
        "identity_proofing_level": allowed_proofing_level,
        "birthdate": "1939-09-26",
        "nhs_number": "9912003888",
        "nonce": "randomnonce",
        "surname": "CARTHY",
        "vot": f"{allowed_proofing_level}.Cp.Cd",
        "family_name": "CARTHY"
    }

    if id_token_claims is not None:
        default_id_token_claims = {**default_id_token_claims, **id_token_claims}

    default_id_token_headers = {"kid": "B86zGrfcoloO13rnjKYDyAJcqj2iZAMrS49jyleL0Fo", "typ": "JWT", "alg": "RS512"}

    if id_token_headers is not None:
        default_id_token_headers = {**default_id_token_headers, **id_token_headers}

    jwt_private_key = _get_nhs_login_private_key()

    return jwt.encode(
        default_id_token_claims, jwt_private_key, algorithm="RS512", headers=default_id_token_headers
    )


def get_token(
    app: Dict, environment: str, _jwt_keys
):
    client_credentials_config = ClientCredentialsConfig(
        environment=environment,
        identity_service_base_url=get_oath_url(environment),
        client_id=app["credentials"][0]["consumerKey"],
        jwt_private_key=_jwt_keys["private_key_pem"],
        jwt_kid="test-1",
    )

    client_credentials_authenticator = ClientCredentialsAuthenticator(config=client_credentials_config)
    token_response = client_credentials_authenticator.get_token()
    assert "access_token" in token_response
    return token_response


def get_authorised_headers(client_app: Dict, environment: str, _jwt_keys):
    token = get_token(app=client_app, environment=environment, _jwt_keys=_jwt_keys)
    return {"Authorization": f'Bearer {token["access_token"]}'}


def get_token_nhs_login_token_exchange(
    test_app,
    environment: str,
    _jwt_keys,
    subject_token_claims: Dict = None
):
    """Call identity server to get an access token"""
    if subject_token_claims is not None:
        id_token_jwt = nhs_login_id_token(
            id_token_claims=subject_token_claims
        )
    else:
        id_token_jwt = nhs_login_id_token()

    # When
    config = TokenExchangeConfig(
        environment=environment,
        identity_service_base_url=get_oath_url(environment),
        client_id=test_app["credentials"][0]["consumerKey"],
        jwt_private_key=_jwt_keys["private_key_pem"],
        jwt_kid="test-1",
        id_token=id_token_jwt,
    )

    authenticator = TokenExchangeAuthenticator(config=config)

    token_resp = authenticator.get_token()

    assert set(token_resp.keys()).issuperset(
        {"access_token", "expires_in", "token_type", "issued_token_type"}
    )
    return token_resp


def _create_app(dev_apps_api: DeveloperAppsAPI, app_name: str, api_products: List[str], app_attrs: Dict,
                jwt_public_key_url: str):
    full_app_attrs = {
        **app_attrs,
        "jwks-resource-url": jwt_public_key_url
    }

    body = {
        "name": app_name,
        "apiProducts": api_products,
        "attributes": [
            {"name": key, "value": value} for key, value in full_app_attrs.items()
        ],
        "scopes": [],
        "status": "approved",
        "callbackUrl": "http://example.com",
        "keyExpiresIn": 60000
    }
    return dev_apps_api.create_app(email=APP_EMAIL, body=body)


def _create_product(product_name: str, products_api: ApiProductsAPI, proxies: List, scopes: List):
    attributes = [
        {"name": "access", "value": "public"},
        {"name": "ratelimit", "value": "300pm"}
    ]
    body = {
        "approvalType": "auto",
        "attributes": attributes,
        "displayName": product_name,
        "environments": ["internal-dev"],
        "name": product_name,
        "proxies": proxies,
        "quota": 300,
        "quotaInterval": "1",
        "quotaTimeUnit": "minute",
        "scopes": scopes
    }

    product = products_api.post_products(body=body)
    return product


@pytest.fixture(scope="session")
def client() -> ApigeeClient:
    config = ApigeeNonProdCredentials()
    return ApigeeClient(config=config)


@pytest.fixture(scope="session")
def environment():
    return get_env("ENVIRONMENT")


@pytest.fixture(scope="session")
def service_name():
    return get_env("FULLY_QUALIFIED_SERVICE_NAME")


@pytest.fixture(scope="session")
def service_url(environment):
    if environment == "prod":
        base_url = "https://api.service.nhs.uk"
    else:
        base_url = f"https://{environment}.api.service.nhs.uk"

    service_base_path = get_env("SERVICE_BASE_PATH")

    return f"{base_url}/{service_base_path}"


@pytest.fixture(scope="session")
def immunisation_history_app(client: ApigeeClient, jwt_public_key_url: str, request):
    """Setup & Teardown an app-restricted app for this api"""
    request_params = request.param

    custom_attributes = {
        "nhs-login-allowed-proofing-level": request_params.get(
            "requested_proofing_level", ""
        ),
    }

    authorised_targets = request_params.get("authorised_targets")
    if authorised_targets is not None:
        custom_attributes["apim-app-flow-vars"] = json.dumps(
            {"immunisation-history": {"authorised_targets": authorised_targets}}
        )

    strict_mode = request_params.get("use_strict_authorised_targets", False)
    if strict_mode:
        custom_attributes["use_strict_authorised_targets"] = strict_mode

    api_products = get_product_names(request_params["suffixes"])

    app_name = f"apim-auto-{uuid4()}"

    developer_apps_api = DeveloperAppsAPI(client=client)
    app = _create_app(dev_apps_api=developer_apps_api, app_name=app_name, api_products=api_products,
                      app_attrs=custom_attributes, jwt_public_key_url=jwt_public_key_url)

    app["request_params"] = request_params
    yield app

    developer_apps_api.delete_app_by_name(email=APP_EMAIL, app_name=app_name)


@pytest.fixture()
def test_product_and_app(client: ApigeeClient, service_name: str, environment: str, jwt_public_key_url: str, request):
    """Setup & Teardown an product and app for this api"""
    request_params = request.param

    products_api = ApiProductsAPI(client=client)
    developer_apps_api = DeveloperAppsAPI(client=client)

    proxies = [f"identity-service-{environment}", f"identity-service-mock-{environment}"]

    if service_name is not None:
        proxies.append(service_name)

    app_name = f"apim-auto-{uuid4()}"
    product_name = f"apim-auto-{uuid4()}"

    product = _create_product(product_name=product_name, products_api=products_api, proxies=proxies,
                              scopes=request_params.get("scopes", []))

    custom_attributes = {
        "nhs-login-allowed-proofing-level": request_params[
            "requested_proofing_level"
        ]
    }

    app = _create_app(dev_apps_api=developer_apps_api, app_name=app_name, api_products=[product_name],
                      app_attrs=custom_attributes, jwt_public_key_url=jwt_public_key_url)
    app["request_params"] = request_params
    yield product, app

    developer_apps_api.delete_app_by_name(email=APP_EMAIL, app_name=app_name)
    products_api.delete_product_by_name(product_name=product_name)

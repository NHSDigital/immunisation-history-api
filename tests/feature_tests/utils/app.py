from contextlib import contextmanager
from typing import List

from pytest_nhsd_apim.auth_journey import create_jwt_key_pair
import json
import base64

from tests.feature_tests.utils.apigee import apigee_request
from tests.feature_tests.utils.constants import (
    ApigeeUrl,
    REDIRECT_URI,
    DYNAMIC_APP_NAME,
    APP_LIFETIME_MILLISECONDS,
    PRODUCT_TYPES, DEFAULT_APP_ATTRIBUTES,
)
from tests.feature_tests.utils.logging import logging


def _get_api_products(api_name: str):
    return [f"{api_name}-{term}" for term in PRODUCT_TYPES]


def jwt_public_key_url(jwt_public_key):
    jwt_public_key_string = json.dumps(jwt_public_key)
    encoded_public_key_bytes = base64.urlsafe_b64encode(jwt_public_key_string.encode())
    return f"https://internal-dev.api.service.nhs.uk/mock-jwks/{encoded_public_key_bytes.decode()}"


def _get_jwks_resource_url(app_restricted: bool, jwt_key_pair) -> str:
    if app_restricted:
        return jwt_public_key_url(jwt_key_pair["json_web_key"])

    return DEFAULT_APP_ATTRIBUTES["jwks-resource-url"]


@logging(teaser="Creating app", kwargs_to_log=["app_name"])
def _create_app(app_name: str, api_products: List[str], app_attrs: dict[str:str], app_restricted: bool):
    jwt_key_pair = create_jwt_key_pair("kid-1")
    full_app_attrs = {
        **app_attrs,
        "jwks-resource-url": _get_jwks_resource_url(app_restricted, jwt_key_pair)
    }

    body = apigee_request(
        method="POST",
        url=ApigeeUrl.CREATE_APP,
        json={
            "name": app_name,
            "attributes": [
                {"name": key, "value": value} for key, value in full_app_attrs.items()
            ],
            "callbackUrl": REDIRECT_URI,
            "keyExpiresIn": APP_LIFETIME_MILLISECONDS,
            "apiProducts": api_products,
            "status": "approved",
        },
    )

    (credentials,) = body["credentials"]
    return {
        "app_key": credentials["consumerKey"],
        "app_secret": credentials["consumerSecret"],
        "jwt_key_pair": jwt_key_pair
    }


@logging(teaser="Deleting app", kwargs_to_log=["app_name"])
def _delete_app(app_name: str):
    return apigee_request(
        method="DELETE", url=ApigeeUrl.DELETE_APP.format(app_name=app_name)
    )


@contextmanager
def app(api_products: list[str], app_attrs: dict[str:str], correlation_id: str, app_restricted: bool = False):
    app_name = DYNAMIC_APP_NAME.format(correlation_id=correlation_id)
    # api_products = _get_api_products(api_name=api_name)

    secrets = _create_app(
        app_name=app_name, api_products=api_products, app_attrs=app_attrs, app_restricted=app_restricted
    )

    exception = None
    try:
        yield secrets
    except Exception as _exception:
        exception = _exception

    _delete_app(app_name=app_name)
    if exception:
        raise Exception

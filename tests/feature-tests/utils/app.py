from contextlib import contextmanager

from utils.apigee import apigee_request
from utils.constants import (
    ApigeeUrl,
    REDIRECT_URI,
    DYNAMIC_APP_NAME,
    APP_LIFETIME_MILLISECONDS,
    PRODUCT_TYPES,
)
from utils.logging import logging


def _get_api_products(api_name: str):
    return [f"{api_name}-{term}" for term in PRODUCT_TYPES]


@logging(teaser="Creating app", kwargs_to_log=["app_name"])
def _create_app(app_name: str, api_products: str, app_attrs: list[dict[str:str]]):
    body = apigee_request(
        method="POST",
        url=ApigeeUrl.CREATE_APP,
        json={
            "name": app_name,
            "attributes": app_attrs,
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
    }


@logging(teaser="Deleting app", kwargs_to_log=["app_name"])
def _delete_app(app_name: str):
    return apigee_request(
        method="DELETE", url=ApigeeUrl.DELETE_APP.format(app_name=app_name)
    )


@contextmanager
def app(api_name: str, app_attrs: list[dict[str:str]], correlation_id: str):
    app_name = DYNAMIC_APP_NAME.format(correlation_id=correlation_id)
    api_products = _get_api_products(api_name=api_name)

    secrets = _create_app(
        app_name=app_name, api_products=api_products, app_attrs=app_attrs
    )

    exception = None
    try:
        yield secrets
    except Exception as _exception:
        exception = _exception

    _delete_app(app_name=app_name)
    if exception:
        raise Exception

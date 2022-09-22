from behave import given, when, then

from tests.feature_tests.utils.app import app
from tests.feature_tests.utils.utils import make_correlation_id, api_name_from_endpoint, proxy_test


@given("A user restricted app with attributes")
def app_attr_user_restricted_app(context):
    context.app_attributes = {
        row["key"]: row["value"] for row in context.table
    }
    context.app_restricted = False


@given("An app restricted app with attributes")
def app_attr_app_restricted_app(context):
    context.app_attributes = {
        row["key"]: row["value"] for row in context.table
    }
    context.app_restricted = True


@given("it has the api products {api_products}")
def set_api_products(context, api_products: str):
    context.api_products = [
        product for product in api_products.split(',')
    ]


@given("it has the following request params")
def set_request_params(context):
    context.request_params = {
        row["key"]: row["value"] for row in context.table
    }


@given("the following headers")
def set_request_headers(context):
    context.request_headers = {
        row["key"]: row["value"] for row in context.table
    }


@when("I make a request to the endpoint FHIR/R4/Immunization")
def make_api_request(context):
    config = {
        "base_url": "https://internal-dev.api.service.nhs.uk",
        "request_config": {
            "url": "https://internal-dev.api.service.nhs.uk/immunisation-history/FHIR/R4/Immunization",
            "params": context.request_params,
            "headers": context.request_headers
        }
    }

    _id = make_correlation_id(context.scenario.name)

    api_name = api_name_from_endpoint("immunisation-history")

    test_kwargs = dict(
        api_name=api_name, correlation_id=_id, app_restricted=context.app_restricted, **config
    )

    api_products = [f"{api_name}-{product}" for product in context.api_products]

    with app(
        api_products=api_products,
        app_attrs=context.app_attributes,
        correlation_id=_id,
        app_restricted=context.app_restricted
    ) as secrets:
        status_code, body = proxy_test(include_trace=False, **secrets, **test_kwargs)

    context.status_code = status_code
    context.body = body


@then("the http response code is {status_code:d}")
def check_response_status(context, status_code):
    assert context.status_code == status_code

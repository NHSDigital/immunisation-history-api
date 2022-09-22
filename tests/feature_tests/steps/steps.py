import json

from behave import given, when, then

from tests.feature_tests.utils.app import app
from tests.feature_tests.utils.utils import make_correlation_id, api_name_from_endpoint, proxy_test, proxy_test_no_oauth


@given("{app_type} restricted app with attributes")
def set_app_attr(context, app_type: str):
    context.app_attributes = {
        row["key"]: row["value"] for row in context.table
    }
    context.app_restricted = False
    if app_type == "app":
        context.app_restricted = True


@given("it has the api products {api_products}")
def set_api_products(context, api_products: str):
    context.api_products = [
        product for product in api_products.split(',')
    ]


@given("the following request params")
def set_request_params(context):
    context.request_params = {
        row["key"]: row["value"] for row in context.table
    }


@given("the following headers")
def set_request_headers(context):
    context.request_headers = {
        row["key"]: row["value"] for row in context.table
    }


@when("I make a request to the endpoint FHIR/R4/Immunization with no oauth token")
def make_api_request_no_auth_token(context):
    config = {
        "base_url": "https://internal-dev.api.service.nhs.uk",
        "request_config": {
            "url": "https://internal-dev.api.service.nhs.uk/immunisation-history/FHIR/R4/Immunization",
            "params": context.request_params,
            "headers": context.request_headers
        }
    }

    context.correlation_id = make_correlation_id(context.scenario.name)

    api_name = api_name_from_endpoint("immunisation-history")

    test_kwargs = dict(
        api_name=api_name, correlation_id=context.correlation_id, app_restricted=context.app_restricted, **config
    )

    api_products = [f"{api_name}-{product}" for product in context.api_products]

    with app(
        api_products=api_products,
        app_attrs=context.app_attributes,
        correlation_id=context.correlation_id,
        app_restricted=context.app_restricted
    ) as secrets:
        status_code, body, headers = proxy_test_no_oauth(include_trace=False, **secrets, **test_kwargs)
        context.response_status_code = status_code
        context.response_body = body
        context.response_headers = headers


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

    context.correlation_id = make_correlation_id(context.scenario.name)

    api_name = api_name_from_endpoint("immunisation-history")

    test_kwargs = dict(
        api_name=api_name, correlation_id=context.correlation_id, app_restricted=context.app_restricted, **config
    )

    api_products = [f"{api_name}-{product}" for product in context.api_products]

    with app(
        api_products=api_products,
        app_attrs=context.app_attributes,
        correlation_id=context.correlation_id,
        app_restricted=context.app_restricted
    ) as secrets:
        status_code, body, headers = proxy_test(include_trace=False, **secrets, **test_kwargs)
        context.response_status_code = status_code
        context.response_body = body
        context.response_headers = headers


@then("the http response code is {status_code:d}")
def check_response_status(context, status_code):
    assert context.response_status_code == status_code, context.response_status_code


@then("the correlation id returned matches the request")
def check_correlation_id(context):
    assert context.correlation_id == context.response_headers["X-Correlation-ID"], context.correlation_id


@then("the error message is {expected_error_msg}")
def check_error_message(context, expected_error_msg: str):
    response_body = json.loads(context.response_body)
    assert response_body["error_description"] == expected_error_msg, response_body


@then("the OperationOutcome error message is {expected_error_msg}")
def check_fhir_error_message(context, expected_error_msg: str):
    actual_error_msg = context.response_body["issue"][0]["diagnostics"]
    assert actual_error_msg == expected_error_msg, context.response_body

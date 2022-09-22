import json
from pathlib import Path

from behave import given, when, then

from tests.feature_tests.utils.app import app
from tests.feature_tests.utils.oauth import get_nhs_login_id_token
from tests.feature_tests.utils.trace import trace, save_trace
from tests.feature_tests.utils.utils import make_correlation_id, api_name_from_endpoint, generate_test_case


@given("apigee app with attributes")
def set_app_attr(context):
    context.app_attributes = {}
    for row in context.table:
        if row["key"] == "use_strict_authorised_targets":
            context.app_attributes[row["key"]] = row["value"] == "True"
        else:
            context.app_attributes[row["key"]] = row["value"]


@given("it has the api products {api_products}")
def set_api_products(context, api_products: str):
    context.api_products = [
        product for product in api_products.split(',')
    ]


@given("it has no api products")
def set_no_api_products(context):
    context.api_products = []


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


@given("the user is authenticated on nhs login with nhs number {nhs_number} and proofing level {proofing_level}")
def set_nhs_login_id_token(context, nhs_number: str, proofing_level: str):
    context.nhs_login_id_token = get_nhs_login_id_token(nhs_number, proofing_level)


@given("no oauth token is provided")
def set_no_oauth(context):
    context.include_oauth = False


@when("I make a request to the endpoint FHIR/R4/Immunization")
def make_api_request(context):
    base_url = "https://internal-dev.api.service.nhs.uk"
    request_config = {
        "url": "https://internal-dev.api.service.nhs.uk/immunisation-history/FHIR/R4/Immunization",
        "params": context.request_params,
        "headers": context.request_headers
    }

    context.correlation_id = make_correlation_id(context.scenario.name)
    api_name = api_name_from_endpoint("immunisation-history")
    api_products = [f"{api_name}-{product}" for product in context.api_products]

    with app(
        api_products=api_products,
        app_attrs=context.app_attributes,
        correlation_id=context.correlation_id
    ) as secrets:
        test_case = generate_test_case(context, secrets, context.correlation_id, context.include_oauth)
        if context.include_trace:
            with trace(api_name=api_name, correlation_id=context.correlation_id) as trace_data:
                status_code, body, headers = test_case(base_url, request_config)
            trace_save_root = Path(__file__).parent
            save_trace(trace_data=trace_data, correlation_id=context.correlation_id, root=trace_save_root)
        else:
            status_code, body, headers = test_case(base_url, request_config)

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
    try:
        response_body = json.loads(context.response_body)
    except TypeError:
        response_body = context.response_body
    assert response_body["error_description"] == expected_error_msg, response_body


@then("the OperationOutcome error message is {expected_error_msg}")
def check_fhir_error_message(context, expected_error_msg: str):
    actual_error_msg = context.response_body["issue"][0]["diagnostics"]
    assert actual_error_msg == expected_error_msg, context.response_body

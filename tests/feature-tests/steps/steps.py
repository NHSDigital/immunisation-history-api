from behave import fixture, given, then, use_fixture, when
from utils.app import app as _app
from utils.utils import api_name_from_endpoint, make_request
from utils.oauth import get_oauth_token


BASE_URL = "https://internal-dev.api.service.nhs.uk"
ENDPOINT = "immunisation-history"


@fixture
def app(context, **kwargs):
    with _app(**kwargs) as secrets:
        context.secrets = secrets
        yield


@given("I will make a request with an app with attributes")
def create_app(context):
    app_attrs = [{"name": row["key"], "value": row["value"]} for row in context.table]

    use_fixture(
        app,
        context,
        api_name=api_name_from_endpoint(ENDPOINT),
        app_attrs=app_attrs,
        correlation_id=context.correlation_id,
    )


@given('the app is authorised according to method "app-restricted"')
def authorise_app(context):
    oauth_token = get_oauth_token(base_url=BASE_URL, **context.secrets)
    context.request_config["headers"]["Authorization"] = f"Bearer {oauth_token}"
    context.request_config["headers"]["x-correlation-id"] = context.correlation_id


@given('the request is to be made to path "{path}"')
def set_request_path(context, path):
    context.request_config["url"] = "/".join((BASE_URL, ENDPOINT, path))


@given("the request will have parameters")
def set_request_params(context):
    context.request_config["params"] = {
        row["key"]: row["value"] for row in context.table
    }


@given("the request will have headers")
def set_request_headers(context):
    headers = {row["key"]: row["value"] for row in context.table}
    context.request_config["headers"].update(headers)


@when('I execute the request via the "{method}" method')
def execute_request(context, method):
    status_code, body = make_request(method=method, **context.request_config)
    context.status_code = status_code
    context.body = body


@then('I get a response with status code "{status_code}"')
def check_status_code(context, status_code):
    assert str(context.status_code) == str(status_code), (
        context.status_code,
        context.body,
    )


@then("the response is valid JSON")
def is_valid_json(context):
    assert type(context.body) is dict

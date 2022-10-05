import json
import re
from datetime import datetime

import requests
from requests.exceptions import HTTPError

from tests.feature_tests.utils.constants import ENVIRONMENT
from tests.feature_tests.utils.logging import logging
from tests.feature_tests.utils.oauth import get_oauth_token


def _snake_case(s: str):
    return "_".join(
        re.sub(
            "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


def _remove_invalid_characters(string: str) -> str:
    return string.replace("@", "").replace(".", "-").replace("~", "")


def make_correlation_id(title: str):
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    snake_title = _snake_case(_remove_invalid_characters(title))
    return f"{snake_title}-{timestamp}"


@logging(teaser="Making request")
def make_request(request_config: dict, correlation_id: str, oauth_token: str = ""):
    if oauth_token:
        request_config["headers"]["Authorization"] = f"Bearer {oauth_token}"
    request_config["headers"]["x-correlation-id"] = correlation_id
    response = requests.get(**request_config)
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = response.text
    return response.status_code, body, response.headers


def api_name_from_endpoint(endpoint):
    return endpoint if "-pr-" in endpoint else f"{endpoint}-{ENVIRONMENT}"


def generate_test_case(context, secrets, correlation_id: str, include_oauth: bool):
    def run_test_case(base_url: str, request_config: dict):
        print(
            "\nRunning test:",
            f"\t- url: {request_config['url']}",
            f"\t- correlation id: {correlation_id}",
            sep="\n",
        )

        app_key = secrets["app_key"]
        app_jwt_private_key = secrets["app_jwt_private_key"]
        try:
            oauth_token = get_oauth_token(base_url, app_key, app_jwt_private_key, context.nhs_login_id_token)
        except HTTPError as e:
            return e.response.status_code, e.response.text, e.response.headers
        except RuntimeError as e:
            error_split = str(e).split(":")
            status_code = int(error_split.pop(0))
            text = ":".join(error_split)
            return status_code, text, {}

        return make_request(request_config, context.correlation_id, oauth_token)

    def run_test_case_no_oauth(base_url: str, request_config: dict):
        print(
            "\nRunning test:",
            f"\t- url: {request_config['url']}",
            f"\t- correlation id: {correlation_id}",
            sep="\n",
        )

        return make_request(request_config, correlation_id)

    if include_oauth:
        return run_test_case

    return run_test_case_no_oauth

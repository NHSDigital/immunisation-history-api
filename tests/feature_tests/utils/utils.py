import json
import re
from datetime import datetime
from pathlib import Path

import requests

from tests.feature_tests.utils.constants import ENVIRONMENT, DEFAULT_APP_ATTRIBUTES
from tests.feature_tests.utils.logging import logging
from tests.feature_tests.utils.oauth import get_oauth_token
from tests.feature_tests.utils.trace import trace, save_trace

ROOT = Path(__file__).parent


def _snake_case(s: str):
    return "_".join(
        re.sub(
            "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


def make_correlation_id(title: str):
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    snake_title = _snake_case(title.replace("@", ""))
    return f"{snake_title}-{timestamp}"


@logging(teaser="Making request")
def make_request(**request_config):
    response = requests.get(**request_config)
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = response.text
    return response.status_code, body


def run_test_case(
    base_url: str,
    request_config: dict,
    app_secret: str,
    app_key: str,
    correlation_id: str,
    jwt_key_pair,
    app_restricted: bool
):
    print(
        "\nRunning test:",
        f"\t- url: {request_config['url']}",
        f"\t- correlation id: {correlation_id}",
        sep="\n",
    )

    oauth_token = get_oauth_token(
        base_url=base_url,
        app_key=app_key,
        app_secret=app_secret,
        jwt_key_pair=jwt_key_pair,
        app_restricted=app_restricted
    )

    request_config["headers"]["Authorization"] = f"Bearer {oauth_token}"
    request_config["headers"]["x-correlation-id"] = correlation_id

    return make_request(**request_config)


def api_name_from_endpoint(endpoint):
    return endpoint if "-pr-" in endpoint else f"{endpoint}-{ENVIRONMENT}"


def parse_app_attributes(app_attributes: dict[str:str]) -> list[dict[str:str]]:
    return [
        {"name": name, "value": value}
        for name, value in {**DEFAULT_APP_ATTRIBUTES, **app_attributes}.items()
    ]


def proxy_test(api_name: str, correlation_id: str, include_trace: bool, **kwargs):
    if include_trace:
        with trace(api_name=api_name, correlation_id=correlation_id) as trace_data:
            status_code, body = run_test_case(correlation_id=correlation_id, **kwargs)
        save_trace(trace_data=trace_data, correlation_id=correlation_id, root=ROOT)
        return status_code, body
    else:
        return run_test_case(correlation_id=correlation_id, **kwargs)

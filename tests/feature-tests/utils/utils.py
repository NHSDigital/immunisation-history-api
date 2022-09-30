import json
import os
import re
from datetime import datetime
from getpass import getpass

import requests
import yaml

from utils.constants import ENVIRONMENT, DEFAULT_APP_ATTRIBUTES
from utils.logging import logging
from utils.oauth import get_oauth_token


def _snake_case(s: str):
    return "_".join(
        re.sub(
            "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


def make_correlation_id(title: str):
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    snake_title = _snake_case(title)
    return f"{snake_title}-{timestamp}"


@logging(teaser="Making request")
def make_request(method, **request_config):
    response = requests.request(method=method, **request_config)
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = response.text
    return response.status_code, body


def run_test_case(
    base_url: str,
    request_config: dict,
    auth_level: str,
    app_secret: str,
    app_key: str,
    correlation_id: str,
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
        # auth_level=auth_level,
    )

    request_config["headers"]["Authorization"] = f"Bearer {oauth_token}"
    request_config["headers"]["x-correlation-id"] = correlation_id

    status_code, body = make_request(**request_config)

    print(
        f"\t- status_code: {status_code}",
        "\t- body:\n",
        body,
        "",
        sep="\n",
    )


def get_secrets(*args: tuple[str]):
    secrets = {
        arg: os.environ.get(arg.upper()) or getpass(prompt=f"{arg}: ") for arg in args
    }
    if not any(secrets.values()):
        raise ValueError("Blank secrets are not permitted")
    return secrets


def load_config(path: str):
    with open(path) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    url_parts = config["request_config"].pop("url")
    config["request_config"]["url"] = "/".join(url_parts.values())
    config["base_url"] = url_parts["base"]
    config["endpoint"] = url_parts["endpoint"]
    config["auth_level"] = config["app_attributes"]["nhs-login-allowed-proofing-level"]
    config["app_attributes"] = parse_app_attributes(
        app_attributes=config.pop("app_attributes", {})
    )
    return config


def api_name_from_endpoint(endpoint):
    return endpoint if "-pr-" in endpoint else f"{endpoint}-{ENVIRONMENT}"


def parse_app_attributes(app_attributes: dict[str:str]) -> list[dict[str:str]]:
    return [
        {"name": name, "value": value}
        for name, value in {**DEFAULT_APP_ATTRIBUTES, **app_attributes}.items()
    ]

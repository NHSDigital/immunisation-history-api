# flake8: noqaimport asyncio
import asyncio
import json
from copy import deepcopy
from typing import Dict, List
from uuid import uuid4

import pytest
import requests

from tests import conftest

TARGET_COMBINATIONS = [["COVID19"], ["HPV", "COVID19"]]

VALID_NHS_NUMBER = "9912003888"


def dict_path(raw, path: List[str]):
    if not raw:
        return raw

    if not path:
        return raw

    res = raw.get(path[0])
    if not res or len(path) == 1 or type(res) != dict:
        return res

    return dict_path(res, path[1:])


def _base_valid_uri(nhs_number) -> str:
    return f"FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|{nhs_number}"


def _valid_uri_procedure_below(nhs_number, procedure_code) -> str:
    return _base_valid_uri(nhs_number) + f"&procedure-code:below={procedure_code}"


def _valid_uri_immunization_target(nhs_number: str, target: str) -> str:
    return _base_valid_uri(nhs_number) + f"&immunization.target={target}"


def _add_authorised_targets_to_request_params(request_params_list: List[Dict]):
    new_request_params_list = []
    for request_params in request_params_list:
        for strict_mode in (True, False):
            for targets in TARGET_COMBINATIONS:
                _request_params = deepcopy(request_params)
                _request_params["authorised_targets"] = targets
                _request_params["use_strict_authorised_targets"] = strict_mode
                new_request_params_list.append(_request_params)
    return new_request_params_list


def _generate_correlation_id(prefix: str) -> str:
    return f'{prefix}_{uuid4()}'


def _assert_unauthorized_client_exception(exc_info):
    message = str(exc_info.value).split(":", 1)
    assert message[0] == "401"  # response status_code
    body = json.loads(message[1])
    assert body["error"] == "unauthorized_client"
    assert (
        body["error_description"]
        == "you have tried to request authorization but your application is not configured to use this authorization grant type"
    )


@pytest.mark.smoketest
def test_ping(service_url):
    resp = requests.get(f"{service_url}/_ping")
    assert resp.status_code == 200


@pytest.mark.smoketest
def test_status(service_url):
    resp = requests.get(f"{service_url}/_status", headers={"apikey": conftest.get_env("STATUS_ENDPOINT_API_KEY")})
    status_json = resp.json()
    assert resp.status_code == 200
    assert status_json["status"] == "pass"


@pytest.mark.smoketest
def test_check_status_is_secured(service_url):
    resp = requests.get(f"{service_url}/_status")
    assert resp.status_code == 401


@pytest.mark.e2e
def test_check_immunization_is_secured(service_url):
    resp = requests.get(f'{service_url}/{_base_valid_uri(VALID_NHS_NUMBER)}')
    assert resp.status_code == 401


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    _add_authorised_targets_to_request_params(
        [
            {"suffixes": ["-application-restricted"]},
            {"suffixes": ["-application-restricted", "-user-restricted"]},
        ]
    ),
    indirect=True,
)
def test_client_credentials_happy_path(immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_client_credentials_happy_path')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,
    )
    body = resp.json()
    assert resp.status_code == 200, body
    assert "x-correlation-id" in resp.headers, resp.headers
    assert resp.headers["x-correlation-id"] == correlation_id
    assert body["resourceType"] == "Bundle", body
    assert len(body["entry"]) == 3, body


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "immunisation_history_app",
    _add_authorised_targets_to_request_params(
        [
            {"suffixes": ["-user-restricted"]},
            {"suffixes": ["-application-restricted"]},
        ]
    ),
    indirect=True,
)
async def test_immunization_no_auth_bearer_token_provided(
    immunisation_history_app: Dict, service_url: str
):
    await asyncio.sleep(1)  # Add delay to tests to avoid 429 on service callout
    correlation_id = _generate_correlation_id('test_immunization_no_auth_bearer_token_provided')
    headers = {"Authorization": "Bearer", "X-Correlation-ID": correlation_id}
    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}', headers=headers,
    )
    assert resp.status_code == 401, "failed getting backend data"
    body = resp.json()
    assert "x-correlation-id" in resp.headers, resp.headers
    assert resp.headers["x-correlation-id"] == correlation_id
    assert body["issue"] == [
        {
            "code": "forbidden",
            "diagnostics": "Provided access token is invalid",
            "severity": "error",
        }
    ], body


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "immunisation_history_app",
    _add_authorised_targets_to_request_params(
        [
            {
                "suffixes": ["-user-restricted"],
                "requested_proofing_level": "P9",
                "identity_proofing_level": "P9",
            }
        ]
    ),
    indirect=True,
)
async def test_bad_nhs_number(immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys):
    await asyncio.sleep(1)  # Add delay to tests to avoid 429 on service callout

    subject_token_claims = {
        "identity_proofing_level": immunisation_history_app["request_params"]["identity_proofing_level"]
    }
    token_response = conftest.get_token_nhs_login_token_exchange(
        test_app=immunisation_history_app, environment=environment, _jwt_keys=_jwt_keys,
        subject_token_claims=subject_token_claims
    )
    correlation_id = _generate_correlation_id('test_bad_nhs_number')

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below("90000000009", "90640007")}',
        headers={
            "Authorization": f'Bearer {token_response["access_token"]}',
            "X-Correlation-ID": correlation_id,
        },
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["resourceType"] == "OperationOutcome", body
    issue = next(
        (i for i in body.get("issue", []) if i.get("severity") == "error"), None
    )
    assert (
        issue.get("diagnostics")
        == "Missing required request parameters: [patient.identifier]"
    ), body


@pytest.mark.e2e
def test_correlation_id_mirrored_in_resp_when_error(service_url):
    access_token = "invalid_token"

    correlation_id = _generate_correlation_id('test_correlation_id_mirrored_in_resp_when_error')

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Correlation-ID": correlation_id,
        },
    )
    assert resp.status_code == 401
    assert "x-correlation-id" in resp.headers, resp.headers
    assert resp.headers["x-correlation-id"] == correlation_id, resp.headers


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    _add_authorised_targets_to_request_params(
        [
            {
                "suffixes": ["-user-restricted"],
                "requested_proofing_level": "P9",
                "identity_proofing_level": "P9",
            },
            {
                "suffixes": ["-user-restricted"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P9",
            },
            {
                "suffixes": ["-user-restricted"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P5",
            },
            {
                "suffixes": ["-application-restricted", "-user-restricted"],
                "requested_proofing_level": "P9",
                "identity_proofing_level": "P9",
            },
            {
                "suffixes": ["-application-restricted", "-user-restricted"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P9",
            },
            {
                "suffixes": ["-application-restricted", "-user-restricted"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P5",
            },
        ]
    ),
    indirect=True,
)
def test_token_exchange_happy_path(immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys):
    subject_token_claims = {
        "identity_proofing_level": immunisation_history_app["request_params"]["identity_proofing_level"]
    }
    token_response = conftest.get_token_nhs_login_token_exchange(
        test_app=immunisation_history_app, environment=environment, _jwt_keys=_jwt_keys,
        subject_token_claims=subject_token_claims
    )
    token = token_response["access_token"]

    correlation_id = _generate_correlation_id('test_token_exchange_happy_path')
    headers = {"Authorization": f"Bearer {token}", "X-Correlation-ID": correlation_id}

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}', headers=headers,
    )
    assert resp.status_code == 200, f'failed getting backend data {immunisation_history_app["request_params"]} {resp}'
    body = resp.json()
    assert "x-correlation-id" in resp.headers, resp.headers
    assert resp.headers["x-correlation-id"] == correlation_id
    assert body["resourceType"] == "Bundle", body
    assert len(body["entry"]) == 3, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    _add_authorised_targets_to_request_params(
        [
            {
                "suffixes": ["-application-restricted"],
                "requested_proofing_level": "P9",
                "identity_proofing_level": "P9",
            },
            {
                "suffixes": ["-application-restricted"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P9",
            },
            {
                "suffixes": ["-application-restricted"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P5",
            }
        ]
    ),
    indirect=True,
)
def test_token_exchange_sad_path(immunisation_history_app: Dict, environment: str, _jwt_keys):
    subject_token_claims = {
        "identity_proofing_level": immunisation_history_app["request_params"]["identity_proofing_level"]
    }
    with pytest.raises(RuntimeError) as exc_info:
        conftest.get_token_nhs_login_token_exchange(test_app=immunisation_history_app, environment=environment,
                                                    _jwt_keys=_jwt_keys,
                                                    subject_token_claims=subject_token_claims)

    _assert_unauthorized_client_exception(exc_info=exc_info)


@pytest.mark.skip(reason="Does not work as-is with mock-auth")
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_product_and_app",
    [
        {
            "scopes": ["urn:nhsd:apim:user-nhs-id:aal3:immunisation-history"],
            "requested_proofing_level": "P9",
            "identity_proofing_level": "P9",
        },
        {
            "scopes": ["urn:nhsd:apim:user-nhs-id:aal3:immunisation-history"],
            "requested_proofing_level": "P5",
            "identity_proofing_level": "P9",
        },
    ],
    indirect=True,
)
async def test_user_restricted_access_not_permitted(test_product_and_app, service_url: str, environment: str):
    await asyncio.sleep(1)  # Add delay to tests to avoid 429 on service callout

    test_product, test_app = test_product_and_app

    token_response = conftest.get_token(app=test_app, environment=environment)

    correlation_id = _generate_correlation_id('test_user_restricted_access_not_permitted')

    authorised_headers = {
        "Authorization": f"Bearer {token_response['access_token']}",
        "NHSD-User-Identity": conftest.nhs_login_id_token(
            allowed_proofing_level=test_app["request_params"]["identity_proofing_level"],
        ),
        "X-Correlation-ID": correlation_id
    }

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers
    )
    assert resp.status_code == 401
    body = resp.json()
    assert body["resourceType"] == "OperationOutcome"
    assert body["issue"][0]["severity"] == "error"
    assert body["issue"][0]["diagnostics"] == "Provided access token is invalid"
    assert body["issue"][0]["code"] == "forbidden"


@pytest.mark.e2e
@pytest.mark.parametrize(
    "test_product_and_app",
    _add_authorised_targets_to_request_params(
        [
            {
                "scopes": ["urn:nhsd:apim:user-nhs-login:P6:immunisation-history"],
                "requested_proofing_level": "P9",
                "identity_proofing_level": "P6",
            },
            {
                "scopes": ["urn:nhsd:apim:user-nhs-login:P6:immunisation-history"],
                "requested_proofing_level": "P5",
                "identity_proofing_level": "P6",
            },
        ]
    ),
    indirect=True,
)
def test_token_exchange_invalid_identity_proofing_level_scope(test_product_and_app, service_url: str, environment: str,
                                                              _jwt_keys):
    test_product, test_app = test_product_and_app
    subject_token_claims = {
        "identity_proofing_level": test_app["request_params"]["identity_proofing_level"]
    }
    token_response = conftest.get_token_nhs_login_token_exchange(
        test_app=test_app, environment=environment, _jwt_keys=_jwt_keys, subject_token_claims=subject_token_claims
    )
    token = token_response["access_token"]

    correlation_id = _generate_correlation_id('test_token_exchange_invalid_identity_proofing_level_scope')
    headers = {"Authorization": f"Bearer {token}", "X-Correlation-ID": correlation_id}

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}', headers=headers,
    )
    assert resp.status_code == 401
    # body = resp.json()
    assert "x-correlation-id" in resp.headers, resp.headers
    assert resp.headers["x-correlation-id"] == correlation_id
    # assert body == {
    #     "issue":
    #         [
    #             {
    #                 "severity": "error",
    #                 "diagnostics": "Provided access token is invalid",
    #                 "code": "forbidden"
    #             }
    #         ],
    #     "resourceType": "OperationOutcome"
    # }


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": None,
            "use_strict_authorised_targets": False,
        }
    ],
    indirect=True,
)
def test_pass_when_auth_targets_is_null(immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_pass_when_auth_targets_is_null')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,
    )
    body = resp.text
    assert resp.status_code == 200, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": None,
            "use_strict_authorised_targets": True,
        }
    ],
    indirect=True,
)
def test_fail_when_auth_targets_is_null_in_strict_mode(
    immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys
):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_fail_when_auth_targets_is_null_in_strict_mode')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,

    )
    body = resp.json()
    assert resp.status_code == 401, body
    assert body == {
        "error": "access_denied",
        "error_description": ("Your permissions have been incorrectly configured "
                              "(Custom Attribute Key-Value pair 'authorised_targets'"
                              " is either blank or does not exist). "
                              "Please contact support, quoting this message.")
    }


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "",
            "use_strict_authorised_targets": True,
        },
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "",
            "use_strict_authorised_targets": False,
        },
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "somethingInvalid",
            "use_strict_authorised_targets": False,
        },
    ],
    indirect=True,
)
def test_fail_when_auth_targets_is_blank_or_invalid(
    immunisation_history_app: Dict, service_url: Dict, environment: str, _jwt_keys
):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_fail_when_auth_targets_is_blank_or_invalid')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,

    )
    body = resp.text
    assert resp.status_code == 401, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "*",
            "use_strict_authorised_targets": False,
        }
    ],
    indirect=True,
)
def test_pass_when_auth_targets_is_star_in_non_strict_mode(
    immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys
):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_pass_when_auth_targets_is_star_in_non_strict_mode')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,
    )
    body = resp.text
    assert resp.status_code == 200, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "*",
            "use_strict_authorised_targets": True,
        }
    ],
    indirect=True,
)
def test_fail_when_auth_targets_is_star_in_strict_mode(
    immunisation_history_app: Dict, service_url: str, environment: str, _jwt_keys
):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_fail_when_auth_targets_is_star_in_strict_mode')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,

    )
    body = resp.text
    assert resp.status_code == 403, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    _add_authorised_targets_to_request_params(
        [
            {"suffixes": ["-application-restricted"]},
        ]
    ),
    indirect=True,
)
@pytest.mark.parametrize(
    "extra_header", ["AUTHORISED_TARGETS", "authorised_targets", "autHORised_TArgets"]
)
def test_fail_when_authorised_targets_header_upper_set_in_good_request(
    immunisation_history_app: Dict, extra_header: str, service_url: str, environment: str, _jwt_keys
):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_fail_when_authorised_targets_header_upper_set_in_good_request')
    authorised_headers["X-Correlation-ID"] = correlation_id
    authorised_headers[extra_header] = "FOO,BAR"

    resp = requests.get(
        f'{service_url}/{_valid_uri_procedure_below(VALID_NHS_NUMBER, "90640007")}',
        headers=authorised_headers,

    )
    body = resp.json()
    assert resp.status_code == 404, body
    assert body == {
        "error": "invalid_request",
        "error_description": "AUTHORISED_TARGETS cannot be provided in headers",
    }


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "*",
            "use_strict_authorised_targets": False,
        }
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "immunization_target", ["COVID19", "HPV"]
)
def test_immunization_target_happy_path(immunisation_history_app: Dict, immunization_target: str, service_url: str,
                                        environment: str, _jwt_keys):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_immunization_target_happy_path')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_immunization_target(VALID_NHS_NUMBER, immunization_target)}',
        headers=authorised_headers,

    )
    body = resp.text
    assert resp.status_code == 200, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "*",
            "use_strict_authorised_targets": False,
        }
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "immunization_target", ["COvID19", "hPV", "RANDOM"]
)
def test_immunization_target_unhappy_path(immunisation_history_app: Dict, immunization_target: str,
                                          service_url: str, environment: str, _jwt_keys):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_immunization_target_unhappy_path')
    authorised_headers["X-Correlation-ID"] = correlation_id

    resp = requests.get(
        f'{service_url}/{_valid_uri_immunization_target(VALID_NHS_NUMBER, immunization_target)}',
        headers=authorised_headers,

    )
    body = resp.text
    assert resp.status_code == 400, body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "immunisation_history_app",
    [
        {
            "suffixes": ["-application-restricted"],
            "authorised_targets": "*",
            "use_strict_authorised_targets": False,
        }
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "immunization_target", ["COVID19", "HPV"]
)
@pytest.mark.parametrize(
    "x_request_url_name", ["X-Request-Url", "X-REQUEST-URL", "x-request-url"]
)
def test_fails_if_request_url_set_in_header(immunisation_history_app: Dict, immunization_target: str,
                                            x_request_url_name: str,
                                            service_url: str, environment: str, _jwt_keys):
    authorised_headers = conftest.get_authorised_headers(client_app=immunisation_history_app, environment=environment,
                                                         _jwt_keys=_jwt_keys)

    correlation_id = _generate_correlation_id('test_fails_if_request_url_set_in_header')
    authorised_headers["X-Correlation-ID"] = correlation_id
    authorised_headers[x_request_url_name] = "this_is_an_injected_url"

    resp = requests.get(
        f'{service_url}/{_valid_uri_immunization_target(VALID_NHS_NUMBER, immunization_target)}',
        headers=authorised_headers,

    )
    body = resp.json()
    assert resp.status_code == 404, body
    assert body == {
        "error": "invalid_request",
        "error_description": "X-Request-Url cannot be provided in headers"
    }

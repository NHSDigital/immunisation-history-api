from typing import List
from uuid import uuid4

import pytest
from aiohttp import ClientResponse
from api_test_utils import env
from api_test_utils import poll_until
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig


def dict_path(raw, path: List[str]):
    if not raw:
        return raw

    if not path:
        return raw

    res = raw.get(path[0])
    if not res or len(path) == 1 or type(res) != dict:
        return res

    return dict_path(res, path[1:])


@pytest.mark.e2e
@pytest.mark.smoketest
def test_output_test_config(api_test_config: APITestSessionConfig):
    print(api_test_config)


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_ping(
    api_client: APISessionClient, api_test_config: APITestSessionConfig
):
    async def apigee_deployed(resp: ClientResponse):
        if resp.status != 200:
            return False
        body = await resp.json()

        return body.get("commitId") == api_test_config.commit_id

    await poll_until(
        make_request=lambda: api_client.get("_ping"), until=apigee_deployed, timeout=30
    )


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_check_status_is_secured(api_client: APISessionClient):

    async with api_client.get("_status", allow_retries=True) as resp:
        assert resp.status == 401


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_status(
    api_client: APISessionClient, api_test_config: APITestSessionConfig
):
    async def is_deployed(resp: ClientResponse):
        if resp.status != 200:
            return False
        body = await resp.json()

        if body.get("commitId") != api_test_config.commit_id:
            return False

        backend = dict_path(body, ["checks", "healthcheck", "outcome", "version"])
        if not backend:
            return True

        return backend.get("commitId") == api_test_config.commit_id

    deploy_timeout = 120 if api_test_config.api_environment.endswith("sandbox") else 30

    await poll_until(
        make_request=lambda: api_client.get(
            "_status", headers={"apikey": env.status_endpoint_api_key()}
        ),
        until=is_deployed,
        timeout=deploy_timeout,
    )


def _base_valid_uri(nhs_number) -> str:
    return f"FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|{nhs_number}"


def _valid_uri(nhs_number, procedure_code) -> str:
    return _base_valid_uri(nhs_number) + f"&procedure-code:below={procedure_code}"


@pytest.fixture(scope='function')
def authorised_headers(valid_access_token):
    return {"Authorization": f"Bearer {valid_access_token}"}


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_check_immunization_is_secured(api_client: APISessionClient):

    async with api_client.get(_base_valid_uri("9912003888"), allow_retries=True) as resp:
        assert resp.status == 401


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_immunization_happy_path(api_client: APISessionClient, authorised_headers):

    correlation_id = str(uuid4())
    authorised_headers["X-Correlation-ID"] = correlation_id

    async with api_client.get(
        _valid_uri("9912003888", "90640007"),
        headers=authorised_headers,
        allow_retries=True
    ) as resp:
        assert resp.status == 200
        body = await resp.json()
        assert "x-correlation-id" in resp.headers, resp.headers
        assert resp.headers["x-correlation-id"] == correlation_id
        assert body["resourceType"] == "Bundle", body
        # no data for this nhs number ...
        assert len(body["entry"]) == 0, body


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_bad_nhs_number(api_client: APISessionClient, authorised_headers):

    async with api_client.get(
        _valid_uri("90000000009", "90640007"),
        headers=authorised_headers,
        allow_retries=True
    ) as resp:
        assert resp.status == 400

        body = await resp.json()
        assert body["resourceType"] == "OperationOutcome", body
        issue = next((i for i in body.get('issue', []) if i.get('severity') == 'error'), None)
        assert issue.get("diagnostics") == "Missing or invalid NHS number", body


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_correlation_id_mirrored_in_resp_when_error(
    api_client: APISessionClient
):
    access_token = "invalid_token"

    correlation_id = str(uuid4())

    async with api_client.get(
        _valid_uri("9912003888", "90640007"),
        headers={"Authorization": f"Bearer {access_token}", "X-Correlation-ID": correlation_id},
        allow_retries=True
    ) as resp:
        assert resp.status == 401
        assert "x-correlation-id" in resp.headers, resp.headers
        assert resp.headers["x-correlation-id"] == correlation_id, resp.headers

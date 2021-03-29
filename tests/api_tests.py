from typing import List

import pytest
from time import time
from uuid import uuid4
from aiohttp import ClientResponse
from api_test_utils import poll_until, is_401
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils import env
from .configuration.environment import ENV


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
        make_request=lambda: api_client.get("_ping"), until=apigee_deployed, timeout=10
    )


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_check_status_is_secured(api_client: APISessionClient):
    await poll_until(
        make_request=lambda: api_client.get("_status"), until=is_401, timeout=10
    )


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

    await poll_until(
        make_request=lambda: api_client.get(
            "_status", headers={"apikey": env.status_endpoint_api_key()}
        ),
        until=is_deployed,
        timeout=10,
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_check_immunization_is_secured(api_client: APISessionClient):
    await poll_until(
        make_request=lambda: api_client.get(
            "FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|9912003888"
        ),
        until=is_401,
        timeout=10,
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_immunization_happy_path(
    api_client: APISessionClient, test_app, get_token
):
    jwt = test_app.oauth.create_jwt(
        **{
            "kid": "test-1",
            "claims": {
                "sub": test_app.client_id,
                "iss": test_app.client_id,
                "jti": str(uuid4()),
                "aud": ENV["token_url"],
                "exp": int(time()) + 5,
            },
        }
    )
    token = await get_token(test_app, grant_type="client_credentials", _jwt=jwt)
    access_token = token["access_token"]

    async def is_happy_path(resp: ClientResponse):
        if resp.status != 200:
            return False
        body = await resp.json()
        return body["resourceType"] == "Bundle" and len(body["entry"]) >= 1

    await poll_until(
        make_request=lambda: api_client.get(
            "FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|9912003888",
            headers={"Authorization": f"Bearer {access_token}"},
        ),
        until=is_happy_path,
        timeout=10,
    )


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.skip  # Won't work while there's a dummy endpoint
async def test_immunization_empty_path(
    api_client: APISessionClient, test_app, get_token
):
    jwt = test_app.oauth.create_jwt(
        **{
            "kid": "test-1",
            "claims": {
                "sub": test_app.client_id,
                "iss": test_app.client_id,
                "jti": str(uuid4()),
                "aud": ENV["token_url"],
                "exp": int(time()) + 5,
            },
        }
    )
    token = await get_token(test_app, grant_type="client_credentials", _jwt=jwt)
    access_token = token["access_token"]

    async def is_happy_path(resp: ClientResponse):
        if resp.status != 200:
            return False
        body = await resp.json()
        return body["resourceType"] == "Bundle" and len(body["entry"]) == 0

    await poll_until(
        make_request=lambda: api_client.get(
            "FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|90000000009",
            headers={"Authorization": f"Bearer {access_token}"},
        ),
        until=is_happy_path,
        timeout=10,
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_correlation_id_mirrored_in_resp_happy_path(
    api_client: APISessionClient, test_app, get_token
):
    jwt = test_app.oauth.create_jwt(
        **{
            "kid": "test-1",
            "claims": {
                "sub": test_app.client_id,
                "iss": test_app.client_id,
                "jti": str(uuid4()),
                "aud": ENV["token_url"],
                "exp": int(time()) + 5,
            },
        }
    )
    token = await get_token(test_app, grant_type="client_credentials", _jwt=jwt)
    access_token = token["access_token"]

    correlation_id = str(uuid4())

    async def is_happy_path(resp: ClientResponse):
        if resp.status != 200:
            return False

        return resp.headers["x-correlation-id"] == correlation_id

    await poll_until(
        make_request=lambda: api_client.get(
            "FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|9912003888",
            headers={"Authorization": f"Bearer {access_token}", "X-Correlation-ID": correlation_id},
        ),
        until=is_happy_path,
        timeout=10,
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_correlation_id_mirrored_in_resp_when_error(
    api_client: APISessionClient
):
    access_token = "invalid_token"

    correlation_id = str(uuid4())

    resp = await api_client.get(
            "FHIR/R4/Immunization?patient.identifier=https://fhir.nhs.uk/Id/nhs-number|9912003888",
            headers={"Authorization": f"Bearer {access_token}", "X-Correlation-ID": correlation_id},
        )

    return resp.status == 401 and resp.headers["x-correlation-id"] == correlation_id

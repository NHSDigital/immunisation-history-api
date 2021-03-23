from typing import List
import uuid
import pytest
from aiohttp import ClientResponse
from api_test_utils import poll_until, is_401
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils import env


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
async def test_wait_for_ping(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    async def apigee_deployed(resp: ClientResponse):

        if resp.status != 200:
            return False
        body = await resp.json()

        return body.get("commitId") == api_test_config.commit_id

    await poll_until(
        make_request=lambda: api_client.get('_ping'),
        until=apigee_deployed,
        timeout=120
    )


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_check_status_is_secured(api_client: APISessionClient):

    await poll_until(
        make_request=lambda: api_client.get('_status'),
        until=is_401,
        timeout=120
    )


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_status(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    async def is_deployed(resp: ClientResponse):

        if resp.status != 200:
            return False
        body = await resp.json()

        if body.get("commitId") != api_test_config.commit_id:
            return False

        backend = dict_path(body, ['checks', 'healthcheck', 'outcome', 'version'])
        if not backend:
            return True

        return backend.get("commitId") == api_test_config.commit_id

    await poll_until(
        make_request=lambda: api_client.get('_status', headers={'apikey': env.status_endpoint_api_key()}),
        until=is_deployed,
        timeout=120
    )


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_check_for_correlation_id(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    correlation_id = str(uuid.uuid4())

    async def has_returned_correlation_id(resp: ClientResponse):

        headers = resp.headers

        if not headers["X-Correlation-ID"]:
            return False

        return headers["X-Correlation-ID"] == correlation_id

    await poll_until(
        make_request=lambda: api_client.get('_ping', headers={'X-Correlation-ID': correlation_id}),
        until=has_returned_correlation_id,
        timeout=120
    )

# class TestEndpoints:
#
#     @pytest.fixture()
#     def app(self):
#         """
#         Import the test utils module to be able to:
#             - Create apigee test application
#                 - Update custom attributes
#                 - Update custom ratelimits
#                 - Update products to the test application
#         """
#         return ApigeeApiDeveloperApps()
#
#     @pytest.fixture()
#     def product(self):
#         """
#         Import the test utils module to be able to:
#             - Create apigee test product
#                 - Update custom scopes
#                 - Update environments
#                 - Update product paths
#                 - Update custom attributes
#                 - Update proxies to the product
#                 - Update custom ratelimits
#         """
#         return ApigeeApiProducts()
#
#     @pytest.fixture()
#     async def test_app_and_product(self, app, product):
#         """Create a test app and product which can be modified in the test"""
#         await product.create_new_product()
#
#         await app.create_new_app()
#
#         await product.update_scopes([
#             "urn:nhsd:apim:app:level3:immunisation-history",
#             "urn:nhsd:apim:user-nhs-id:aal3:immunisation-history"
#         ])
#         await app.add_api_product([product.name])
#
#         yield product, app
#
#         await app.destroy_app()
#         await product.destroy_product()
#
#     @pytest.fixture()
#     async def get_token(self, test_app_and_product):
#         """Call identity server to get an access token"""
#         test_product, test_app = test_app_and_product
#         oauth = OauthHelper(
#             client_id=test_app.client_id,
#             client_secret=test_app.client_secret,
#             redirect_uri=test_app.callback_url
#             )
#         token_resp = await oauth.get_token_response(grant_type="authorization_code")
#         assert token_resp["status_code"] == 200
#         return token_resp['body']
#
#     def test_user_restricted(self, get_token):
#         """
#         In here you can add tests which call your proxy
#         You can use the 'get_token' fixture to call the proxy with a access token
#         """
#         pass

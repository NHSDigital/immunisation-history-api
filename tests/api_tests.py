from functools import partial

import pytest
from aiohttp import ClientResponse
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils import poll_until


async def _is_deployed(resp: ClientResponse, api_test_config: APITestSessionConfig):

    if resp.status != 200:
        return False
    body = await resp.json()

    return body.get("commitId") == api_test_config.commit_id


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_ping(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    is_deployed = partial(_is_deployed, api_test_config=api_test_config)

    await poll_until(
        make_request=lambda: api_client.get('_status'),
        until=is_deployed,
        timeout=120
    )


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_status(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    is_deployed = partial(_is_deployed, api_test_config=api_test_config)

    await poll_until(
        make_request=lambda: api_client.get('_status'),
        until=is_deployed,
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

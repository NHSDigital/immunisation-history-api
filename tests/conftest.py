# flake8: noqa
import pytest
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils.fixtures import api_client   # pylint: disable=unused-import
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.oauth_helper import OauthHelper
from .configuration.environment import ENV


@pytest.fixture(scope='session')
def api_test_config() -> APITestSessionConfig:
    return APITestSessionConfig()


@pytest.yield_fixture(scope='function')
@pytest.mark.asyncio
async def test_app():
    """Setup & Teardown an app-restricted app for this api"""
    app = ApigeeApiDeveloperApps()
    await app.create_new_app()
    await app.add_api_product(api_products=[ENV["product"]])
    await app.set_custom_attributes(
        {
            'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/'
                                  'identity-service-jwks/main/jwks/internal-dev/'
                                  '9baed6f4-1361-4a8e-8531-1f8426e3aba8.json'
        }
    )
    app.oauth = OauthHelper(app.client_id, app.client_secret, "")
    yield app
    await app.destroy_app()


@pytest.fixture()
def get_token():
    """Get an access or refresh token
    some examples:
        1. access_token via simulated oauth (default)
            get_token()
        2. get access token with a specified timeout value (default is 5 seconds)
            get_token(timeout=500000)  # 5 minuets
        3. refresh_token via simulated oauth
            get_token(grant_type="refresh_token", refresh_token=<refresh_token>)
        4. access_token with JWT
            get_token(grant_type='client_credentials', _jwt=jwt)
    """

    async def _token(
        app: ApigeeApiDeveloperApps, grant_type: str = "authorization_code", **kwargs
    ):
        oauth = app.oauth
        resp = await oauth.get_token_response(grant_type=grant_type, **kwargs)

        if resp['status_code'] != 200:
            message = 'unable to get token'
            raise RuntimeError(f"\n{'*' * len(message)}\n"
                               f"MESSAGE: {message}\n"
                               f"URL: {resp.get('url')}\n"
                               f"STATUS CODE: {resp.get('status_code')}\n"
                               f"RESPONSE: {resp.get('body')}\n"
                               f"HEADERS: {resp.get('headers')}\n"
                               f"{'*' * len(message)}\n")
        return resp['body']
    return _token

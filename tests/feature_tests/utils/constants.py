ENVIRONMENT = "internal-dev"
ORGANISATION = "nhsd-nonprod"
REDIRECT_URI = "http://tempuri.org/callback"
APIM_EMAIL_ADDRESS = "apm-testing-internal-dev@nhs.net"
SSO_LOGIN_URL = "https://login.apigee.com"
DYNAMIC_APP_NAME = "apim-auto-dda-test-app-{correlation_id}"
PRODUCT_TYPES = ("application-restricted", "user-restricted")
APP_LIFETIME_MILLISECONDS = 60000
TRACE_LIFETIME_SECONDS = 30


class ApigeeUrl:
    _BASE = f"https://api.enterprise.apigee.com/v1/organizations/{ORGANISATION}"
    _REVISIONS_SLUG = "apis/{api_name}/revisions"
    CREATE_APP = f"{_BASE}/developers/{APIM_EMAIL_ADDRESS}/apps"
    DELETE_APP = CREATE_APP + "/{app_name}"
    LIST_REVISIONS = f"{_BASE}/{_REVISIONS_SLUG}/"
    CREATE_TRACE_SESSION = (
        f"{_BASE}/environments/{ENVIRONMENT}/{_REVISIONS_SLUG}"
        + "/{revision}/debugsessions"
    )
    GET_TRACE_DATA = CREATE_TRACE_SESSION + "/{session_name}/data"
    LIST_PRODUCTS = f"{_BASE}/apiproducts"

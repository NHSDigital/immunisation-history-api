import os
from functools import cache

import requests
import sh

from utils.constants import SSO_LOGIN_URL


@cache
def _get_token():
    response = sh.bash("get_token", _env={"SSO_LOGIN_URL": SSO_LOGIN_URL, **os.environ})
    return response.split("\n")[0]


def _apigee_session_header():
    return {"Authorization": f"Bearer {_get_token()}"}


def apigee_request(method: str, url: str, **kwargs) -> dict:
    headers = _apigee_session_header()
    r = requests.request(method=method, url=url, headers=headers, **kwargs)

    try:
        r.raise_for_status()
    except requests.HTTPError as exc:
        print()
        print("An error occurred:")
        print(r.request.url)
        print(r.text)
        print()
        raise exc

    return r.json()

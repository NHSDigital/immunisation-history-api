import os


def get_env(variable_name: str) -> str:
    """Returns a environment variable"""
    try:
        var = os.environ[variable_name]
        if not var:
            raise RuntimeError(f"Variable is null, Check {variable_name}.")
        return var
    except KeyError:
        raise RuntimeError(f"Variable is not set, Check {variable_name}.")


oauth_proxy = get_env("OAUTH_PROXY")
oauth_base_uri = get_env("OAUTH_BASE_URI")

ENV = {
    "product": get_env("APIGEE_PRODUCT"),
    "oauth_proxy": oauth_proxy,
    "oauth_base_uri": oauth_base_uri,
    "token_url": f"{oauth_base_uri}/{oauth_proxy}/token"
}

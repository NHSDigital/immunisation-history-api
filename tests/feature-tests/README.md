Ripped from https://nhsd-git.digital.nhs.uk/data-services/dps-direct-data-access-api/spikes/proxy_tests

## Pre-requisites

- Chrome
- Account on the [internal developer portal](https://internal-portal.developer.nhs.uk/)
- Access to [Apigee](https://apigee.com/organizations/nhsd-nonprod/proxies)
- Install and first time setup of [Apigee's `get_token`](https://docs.apigee.com/api-platform/system-administration/using-gettoken) (make sure to set `export SSO_LOGIN_URL="https://login.apigee.com"` before setup, and your username and password are the same credentials you use for logging into Apigee).

## First time setup

### Setup your virtual env

```
pipenv install
```

## Usage

- Activate your virtual env:

```
source .venv/bin/activate
```

- Run behave

```
behave
```

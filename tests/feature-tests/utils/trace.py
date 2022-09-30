import json
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from utils.apigee import apigee_request
from utils.constants import ApigeeUrl, TRACE_LIFETIME_SECONDS
from utils.logging import logging


def _apim_session_name() -> str:
    return f"apim-auto-{uuid4()}"


def _get_latest_revision(api_name: str) -> int:
    all_revisions_as_strings = apigee_request(
        method="GET", url=ApigeeUrl.LIST_REVISIONS.format(api_name=api_name)
    )
    return max(map(int, all_revisions_as_strings))


@logging(teaser="Creating trace session")
def _create_trace_session(api_name: str) -> dict[str:str]:
    session_name = _apim_session_name()
    revision = _get_latest_revision(api_name)
    params = {"session": session_name, "timeout": str(TRACE_LIFETIME_SECONDS)}
    url = ApigeeUrl.CREATE_TRACE_SESSION.format(api_name=api_name, revision=revision)
    apigee_request(method="POST", url=url, params=params)
    return dict(api_name=api_name, revision=revision, session_name=session_name)


@logging(teaser="Getting trace session data")
def _get_trace_session_data(api_name, revision, session_name):
    url = ApigeeUrl.GET_TRACE_DATA.format(
        api_name=api_name, revision=revision, session_name=session_name
    )
    event_ids = apigee_request(method="GET", url=url)
    data = [
        apigee_request(method="GET", url=url + f"/{event_id}") for event_id in event_ids
    ]
    return data


@contextmanager
def trace(api_name: str, correlation_id: str):
    trace_session_metadata = _create_trace_session(api_name=api_name)

    trace_data = []
    yield trace_data

    _trace_data = _get_trace_session_data(**trace_session_metadata)
    trace_data += list(
        event for event in _trace_data if correlation_id in json.dumps(event)
    )


@logging("Saving trace data")
def save_trace(trace_data: list, root: Path, correlation_id: str):
    path = root / "traces" / f"{correlation_id}.json"
    with open(path, "w") as f:
        json.dump(obj=trace_data, fp=f, indent=2)
    print(path, end=" ")

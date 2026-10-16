from unittest.mock import Mock

import pytest
import requests

from tvsummary.errors import DownloadError, ResponseShapeError
from tvsummary.sources import ShowSource


def test_fetch_records_success(monkeypatch: pytest.MonkeyPatch) -> None:
    response = Mock()
    response.json.return_value = [{"name": "Test Show"}]
    get = Mock(return_value=response)
    monkeypatch.setattr("tvsummary.sources.requests.get", get)

    source = ShowSource(url="https://example.com/shows", timeout=5)
    shows = source.fetch_records()

    assert len(shows) == 1
    assert shows[0].name == "Test Show"
    get.assert_called_once_with("https://example.com/shows", timeout=5)
    response.raise_for_status.assert_called_once_with()


def test_fetch_records_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = requests.ConnectionError("Connection failed")
    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        Mock(side_effect=original),
    )

    with pytest.raises(DownloadError, match="Could not download") as caught:
        ShowSource().fetch_records()

    assert caught.value.__cause__ is original


def test_fetch_records_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    response = Mock()
    original = requests.HTTPError("Server error")
    response.raise_for_status.side_effect = original
    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        Mock(return_value=response),
    )

    with pytest.raises(DownloadError, match="Could not download") as caught:
        ShowSource().fetch_records()

    assert caught.value.__cause__ is original
    response.json.assert_not_called()


def test_fetch_records_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    response = Mock()
    original = ValueError("Invalid JSON")
    response.json.side_effect = original
    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        Mock(return_value=response),
    )

    with pytest.raises(ResponseShapeError, match="not valid JSON") as caught:
        ShowSource().fetch_records()

    assert caught.value.__cause__ is original


@pytest.mark.parametrize("payload", [{}, None, "unexpected"])
def test_fetch_records_requires_list(
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
) -> None:
    response = Mock()
    response.json.return_value = payload
    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        Mock(return_value=response),
    )

    with pytest.raises(ResponseShapeError, match="Expected a list"):
        ShowSource().fetch_records()


def test_fetch_records_skips_invalid_objects(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    response = Mock()
    response.json.return_value = [
        {"name": "First Show"},
        "not a record",
        {"name": "Second Show"},
    ]
    monkeypatch.setattr(
        "tvsummary.sources.requests.get",
        Mock(return_value=response),
    )

    with caplog.at_level("DEBUG", logger="tvsummary.sources"):
        shows = ShowSource().fetch_records()

    assert [show.name for show in shows] == ["First Show", "Second Show"]

    messages = [
        (record.levelname, record.getMessage())
        for record in caplog.records
        if record.name == "tvsummary.sources"
    ]

    assert ("INFO", "Downloading TV show records.") in messages
    assert ("DEBUG", "Processing record at index 0.") in messages
    assert ("WARNING", "Skipping invalid record at index 1.") in messages
    assert ("INFO", "Loaded 2 valid TV show records.") in messages

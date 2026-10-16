import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from tvsummary.errors import DownloadError, ReportError, ResponseShapeError
from tvsummary.main import main


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    path = tmp_path / "settings.toml"
    path.write_text(
        'url = "https://example.com/shows"\n'
        "timeout = 5\n"
        'output_folder = "output"\n'
        "seed = 42\n"
        "sample_size = 1\n"
        'log_level = "INFO"\n',
        encoding="utf-8",
    )
    return path


def test_main_success(
    tmp_path: Path,
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    response = Mock()
    response.json.return_value = [{"name": "Test Show"}]
    get = Mock(return_value=response)
    monkeypatch.setattr("tvsummary.sources.requests.get", get)

    result = main(["--config", str(config_path)])

    assert result == 0
    get.assert_called_once_with("https://example.com/shows", timeout=5.0)

    summary = json.loads(
        (tmp_path / "output" / "summary.json").read_text(encoding="utf-8")
    )
    assert summary["records_processed"] == 1
    assert summary["featured_shows"] == ["Test Show"]
    assert (tmp_path / "output" / "run_info.json").is_file()

    captured = capsys.readouterr()
    assert "Processed 1 shows." in captured.out
    assert "Summary saved to" in captured.out
    assert captured.err == ""


def test_main_missing_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    get = Mock()
    monkeypatch.setattr("tvsummary.sources.requests.get", get)

    result = main(["--config", str(tmp_path / "missing.toml")])

    assert result == 1
    get.assert_not_called()

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Error: Could not read the settings file.\n"
    assert "Traceback" not in captured.err
    assert any(
        record.levelname == "ERROR" and "Application stopped" in record.getMessage()
        for record in caplog.records
    )


@pytest.mark.parametrize(
    "error",
    [
        DownloadError("Download failed."),
        ResponseShapeError("Invalid response."),
        ReportError("Saving failed."),
    ],
)
def test_main_expected_failure(
    error: Exception,
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(
        "tvsummary.main.ShowSource.fetch_records",
        Mock(side_effect=error),
    )

    result = main(["--config", str(config_path)])

    assert result == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"Error: {error}\n"
    assert "Traceback" not in captured.err
    assert any(
        record.levelname == "ERROR" and "Application stopped" in record.getMessage()
        for record in caplog.records
    )

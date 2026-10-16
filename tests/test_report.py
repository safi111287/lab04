import json
from pathlib import Path

import pytest

from tvsummary.config import Settings
from tvsummary.errors import ReportError
from tvsummary.models import Show
from tvsummary.report import build_summary, write_run_info, write_summary


def test_build_summary(sample_shows: list[Show]) -> None:
    summary = build_summary(sample_shows)

    assert summary["records_processed"] == 3
    assert summary["shows_per_genre"] == {"Drama": 2, "Comedy": 1}
    assert summary["average_rating_by_language"] == {"English": 7.0}


def test_write_summary_creates_folder(tmp_path: Path) -> None:
    output = tmp_path / "processed" / "summary.json"
    summary: dict[str, object] = {"records_processed": 3}

    assert write_summary(summary, output) is True
    assert json.loads(output.read_text(encoding="utf-8")) == summary


def test_write_summary_translates_os_error(tmp_path: Path) -> None:
    blocked_folder = tmp_path / "blocked"
    blocked_folder.write_text("This is a file.", encoding="utf-8")
    output = blocked_folder / "summary.json"

    with pytest.raises(ReportError, match="Could not save") as caught:
        write_summary({}, output)

    assert isinstance(caught.value.__cause__, OSError)


def test_summary_uses_settings(sample_shows: list[Show]) -> None:
    settings = Settings(
        url="https://example.com/shows",
        timeout=5.0,
        output_folder=Path("output"),
        seed=42,
        sample_size=2,
        log_level="INFO",
    )

    summary = build_summary(sample_shows, settings)
    repeated = build_summary(sample_shows, settings)
    original = build_summary(sample_shows)

    assert summary["source_url"] == settings.url
    assert summary["featured_shows"] == repeated["featured_shows"]
    assert len(summary["featured_shows"]) == 2

    for key, value in original.items():
        if key != "source_url":
            assert summary[key] == value


def test_write_run_info(tmp_path: Path) -> None:
    settings = Settings(
        url="https://example.com/shows",
        timeout=5.0,
        output_folder=tmp_path,
        seed=42,
        sample_size=2,
        log_level="INFO",
    )

    assert write_run_info(settings) is True

    data = json.loads((tmp_path / "run_info.json").read_text(encoding="utf-8"))

    assert data["settings"]["seed"] == 42
    assert data["settings"]["sample_size"] == 2
    assert data["settings"]["output_folder"] == str(tmp_path)
    assert data["python_version"]
    assert set(data["tool_versions"]) == {"pytest", "mypy", "ruff"}
    assert all(data["tool_versions"].values())


def test_report_logs_progress(
    sample_shows: list[Show],
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level("DEBUG", logger="tvsummary.report"):
        summary = build_summary(sample_shows)
        write_summary(summary, tmp_path / "summary.json")

    assert "Building summary for 3 records." in caplog.text
    assert "Computing aggregation shows_per_genre." in caplog.text
    assert "Saved JSON output" in caplog.text

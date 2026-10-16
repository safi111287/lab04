import json
from pathlib import Path

import pytest

from tvsummary.errors import ReportError
from tvsummary.models import Show
from tvsummary.report import build_summary, write_summary


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
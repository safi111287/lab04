import json
import logging
import platform
from dataclasses import asdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .aggregations import (
    AverageRatingByLanguage,
    DataQuirks,
    ShowsPerDecade,
    ShowsPerGenre,
    ShowsPerNetwork,
)
from .config import OUTPUT_PATH, SOURCE_URL, Settings
from .errors import ReportError
from .models import Show
from .sampling import select_featured_shows

logger = logging.getLogger(__name__)


def build_summary(
    records: list[Show], settings: Settings | None = None
) -> dict[str, object]:
    """Combine aggregations and optionally add featured shows."""
    logger.info("Building summary for %s records.", len(records))
    summary: dict[str, object] = {
        "source_url": settings.url if settings is not None else SOURCE_URL,
        "records_processed": len(records),
    }

    aggregations = [
        ShowsPerGenre(),
        AverageRatingByLanguage(),
        ShowsPerNetwork(),
        ShowsPerDecade(),
        DataQuirks(),
    ]

    for aggregation in aggregations:
        logger.debug("Computing aggregation %s.", aggregation.key)
        summary[aggregation.key] = aggregation.compute(records)

    if settings is not None:
        summary["featured_shows"] = select_featured_shows(
            records, settings.seed, settings.sample_size
        )

    return summary


def write_summary(summary: dict[str, object], path: Path = OUTPUT_PATH) -> bool:
    """Write JSON output or raise a report error."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2)

    except OSError as error:
        raise ReportError("Could not save the summary file.") from error

    logger.info("Saved JSON output to %s.", path)

    return True


def build_run_info(settings: Settings) -> dict[str, object]:
    """Record settings and versions used for this run."""
    settings_data = asdict(settings)
    settings_data["output_folder"] = str(settings.output_folder)

    tool_versions: dict[str, str] = {}
    for package in ("pytest", "mypy", "ruff"):
        try:
            tool_versions[package] = version(package)
        except PackageNotFoundError:
            tool_versions[package] = "not installed"

    return {
        "settings": settings_data,
        "python_version": platform.python_version(),
        "tool_versions": tool_versions,
    }


def write_run_info(settings: Settings) -> bool:
    """Save run information beside the summary."""
    path = settings.output_folder / "run_info.json"
    return write_summary(build_run_info(settings), path)

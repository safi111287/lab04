import json
from pathlib import Path

from .aggregations import (
    AverageRatingByLanguage,
    DataQuirks,
    ShowsPerDecade,
    ShowsPerGenre,
    ShowsPerNetwork,
)
from .config import OUTPUT_PATH, SOURCE_URL
from .errors import ReportError
from .models import Show


def build_summary(records: list[Show]) -> dict[str, object]:
    """Combine all aggregations into one summary."""
    summary: dict[str, object] = {
        "source_url": SOURCE_URL,
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
        summary[aggregation.key] = aggregation.compute(records)

    return summary


def write_summary(summary: dict[str, object], path: Path = OUTPUT_PATH) -> bool:
    """Write the summary or raise a report error."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2)

    except OSError as error:
        raise ReportError("Could not save the summary file.") from error

    return True

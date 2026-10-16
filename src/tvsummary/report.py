import json

from .aggregations import (
    AverageRatingByLanguage,
    DataQuirks,
    ShowsPerDecade,
    ShowsPerGenre,
    ShowsPerNetwork,
)
from .config import OUTPUT_PATH, SOURCE_URL


def build_summary(records):
    """Combine all aggregations into one summary."""
    summary = {
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


def write_summary(summary, path=OUTPUT_PATH):
    """Write the summary to a JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2)

    except OSError as error:
        print(f"Could not write summary to {path}: {error}")
        return False

    return True

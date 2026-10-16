"""Package for summarizing TV show data."""

from .aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    DataQuirks,
    ShowsPerDecade,
    ShowsPerGenre,
    ShowsPerNetwork,
)
from .models import Show
from .report import build_summary, write_summary
from .sources import DownloadError, ShowSource

__all__ = [
    "Aggregation",
    "AverageRatingByLanguage",
    "DataQuirks",
    "DownloadError",
    "Show",
    "ShowSource",
    "ShowsPerDecade",
    "ShowsPerGenre",
    "ShowsPerNetwork",
    "build_summary",
    "write_summary",
]

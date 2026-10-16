"""Define errors that the TV summary application can report."""


class TVSummaryError(Exception):
    """Base class for expected application errors."""


class DownloadError(TVSummaryError):
    """Raised when downloading TV show data fails."""


class ResponseShapeError(TVSummaryError):
    """Raised when downloaded data has an unexpected structure."""


class SettingsError(TVSummaryError):
    """Raised when configuration is missing or invalid."""


class ReportError(TVSummaryError):
    """Raised when saving an output file fails."""

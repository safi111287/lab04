import logging

import requests

from .config import SOURCE_URL, TIMEOUT
from .errors import DownloadError, ResponseShapeError
from .models import Show

logger = logging.getLogger(__name__)


class ShowSource:
    """Download TVMaze records and return Show objects."""

    def __init__(
        self,
        url: str = SOURCE_URL,
        timeout: float = TIMEOUT,
    ) -> None:
        self.url = url
        self.timeout = timeout

    def fetch_records(self) -> list[Show]:
        """Download records and skip invalid record objects."""
        logger.info("Downloading TV show records.")

        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as error:
            raise DownloadError("Could not download TV show data.") from error

        try:
            records = response.json()
        except ValueError as error:
            raise ResponseShapeError(
                "The server response is not valid JSON."
            ) from error

        if not isinstance(records, list):
            raise ResponseShapeError("Expected a list of TV show records.")

        shows: list[Show] = []

        for index, record in enumerate(records):
            if not isinstance(record, dict):
                logger.warning("Skipping invalid record at index %s.", index)
                continue

            logger.debug("Processing record at index %s.", index)
            shows.append(Show(record))

        logger.info("Loaded %s valid TV show records.", len(shows))
        return shows

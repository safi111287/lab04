import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging from the entry point."""
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )

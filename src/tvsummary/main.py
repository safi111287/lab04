import argparse
import logging
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH, load_settings
from .errors import TVSummaryError
from .logging_setup import configure_logging
from .report import build_summary, write_run_info, write_summary
from .sources import ShowSource

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Run the application and return its exit code."""
    parser = argparse.ArgumentParser(description="Summarize TVMaze show data.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the TOML settings file.",
    )
    args = parser.parse_args(argv)

    log_level = "INFO"
    try:
        settings = load_settings(args.config)
        log_level = settings.log_level
    except TVSummaryError as error:
        configure_logging(log_level)
        logger.error("Application stopped: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return 1

    configure_logging(log_level)

    try:
        logger.info("Starting TV show summary.")
        source = ShowSource(url=settings.url, timeout=settings.timeout)
        records = source.fetch_records()
        summary = build_summary(records, settings)

        output_path = settings.output_folder / "summary.json"
        write_summary(summary, output_path)
        write_run_info(settings)

    except TVSummaryError as error:
        logger.error("Application stopped: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Processed {len(records)} shows.")
    print(f"Summary saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

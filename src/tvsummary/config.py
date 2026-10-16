import math
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .errors import SettingsError

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
TIMEOUT = 10
OUTPUT_PATH = Path("data/processed/summary.json")
DEFAULT_CONFIG_PATH = Path("config/tvsummary.toml")


@dataclass(frozen=True)
class Settings:
    """Store validated application settings."""

    url: str
    timeout: float
    output_folder: Path
    seed: int
    sample_size: int
    log_level: str


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> Settings:
    """Read and validate all required TOML settings."""
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except OSError as error:
        raise SettingsError("Could not read the settings file.") from error
    except tomllib.TOMLDecodeError as error:
        raise SettingsError("The settings file is not valid TOML.") from error

    required = (
        "url",
        "timeout",
        "output_folder",
        "seed",
        "sample_size",
        "log_level",
    )

    for key in required:
        if key not in data:
            raise SettingsError(f"Missing required setting: {key}")

    url = data["url"]
    if not isinstance(url, str) or not url.strip():
        raise SettingsError("url must be a non-empty HTTP or HTTPS URL.")

    try:
        parsed_url = urlsplit(url)
        valid_url = parsed_url.scheme in {"http", "https"} and parsed_url.hostname
    except ValueError as error:
        raise SettingsError("url must be a valid HTTP or HTTPS URL.") from error

    if not valid_url:
        raise SettingsError("url must be a valid HTTP or HTTPS URL.")

    timeout = data["timeout"]
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise SettingsError("timeout must be a positive finite number.")

    output_folder = data["output_folder"]
    if not isinstance(output_folder, str) or not output_folder.strip():
        raise SettingsError("output_folder must be a non-empty path.")

    seed = data["seed"]
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise SettingsError("seed must be an integer.")

    sample_size = data["sample_size"]
    if (
        isinstance(sample_size, bool)
        or not isinstance(sample_size, int)
        or sample_size < 0
    ):
        raise SettingsError("sample_size must be a non-negative integer.")

    log_level = data["log_level"]
    allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if not isinstance(log_level, str) or log_level.upper() not in allowed_levels:
        raise SettingsError("log_level must be a valid logging level.")

    return Settings(
        url=url,
        timeout=float(timeout),
        output_folder=Path(output_folder),
        seed=seed,
        sample_size=sample_size,
        log_level=log_level.upper(),
    )

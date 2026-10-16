import tomllib
from pathlib import Path

import pytest

from tvsummary.config import load_settings
from tvsummary.errors import SettingsError

VALID_CONFIG = """\
url = "https://api.tvmaze.com/shows?page=0"
timeout = 10
output_folder = "data/processed"
seed = 42
sample_size = 5
log_level = "INFO"
"""


def test_load_valid_settings(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(VALID_CONFIG, encoding="utf-8")

    settings = load_settings(path)

    assert settings.url == "https://api.tvmaze.com/shows?page=0"
    assert settings.timeout == 10.0
    assert settings.output_folder == Path("data/processed")
    assert settings.seed == 42
    assert settings.sample_size == 5
    assert settings.log_level == "INFO"


def test_missing_settings_file(tmp_path: Path) -> None:
    with pytest.raises(SettingsError, match="Could not read") as caught:
        load_settings(tmp_path / "missing.toml")

    assert isinstance(caught.value.__cause__, OSError)


def test_invalid_toml(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text("timeout = [", encoding="utf-8")

    with pytest.raises(SettingsError, match="not valid TOML") as caught:
        load_settings(path)

    assert isinstance(caught.value.__cause__, tomllib.TOMLDecodeError)


@pytest.mark.parametrize(
    "key",
    ["url", "timeout", "output_folder", "seed", "sample_size", "log_level"],
)
def test_missing_required_setting(tmp_path: Path, key: str) -> None:
    path = tmp_path / "settings.toml"
    lines = [
        line for line in VALID_CONFIG.splitlines() if not line.startswith(f"{key} =")
    ]
    path.write_text("\n".join(lines), encoding="utf-8")

    with pytest.raises(SettingsError, match=f"Missing required setting: {key}"):
        load_settings(path)


@pytest.mark.parametrize(
    ("original", "replacement", "message"),
    [
        ("timeout = 10", "timeout = 0", "timeout must"),
        ("timeout = 10", "timeout = true", "timeout must"),
        ("timeout = 10", "timeout = inf", "timeout must"),
        ('url = "https://api.tvmaze.com/shows?page=0"', 'url = "invalid"', "url must"),
        (
            'output_folder = "data/processed"',
            'output_folder = ""',
            "output_folder must",
        ),
        ("seed = 42", 'seed = "wrong"', "seed must"),
        ("sample_size = 5", "sample_size = -1", "sample_size must"),
        ('log_level = "INFO"', 'log_level = "wrong"', "log_level must"),
    ],
)
def test_invalid_setting(
    tmp_path: Path,
    original: str,
    replacement: str,
    message: str,
) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(
        VALID_CONFIG.replace(original, replacement),
        encoding="utf-8",
    )

    with pytest.raises(SettingsError, match=message):
        load_settings(path)

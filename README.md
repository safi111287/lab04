# TV Show Summary — Lab 04

This Python package downloads TVMaze show records and creates a JSON summary.  
It includes offline tests, custom errors, logging, type annotations, TOML settings,  
and repeatable featured-show sampling.

## Setup

Run these commands from an Anaconda Prompt:

```bash
git clone https://github.com/safi111287/lab04.git test-lab04-clone
cd test-lab04-clone
conda env create -f environment.yml
conda activate tvsummary-lab04
python -m pip install -r requirements.txt
python -m pip install -e .
```

The environment uses Python 3.11. Direct dependencies and checking tools are
pinned in requirements.txt.

## Run

Run commands from the repository root.

Use the default settings file, config/tvsummary.toml:

```bash
python -m tvsummary.main
```

Choose a settings file explicitly:

```bash
python -m tvsummary.main --config config/tvsummary.toml
```

The root entry point also works:

```bash
python main.py
```

With the supplied settings, the program writes:

- data/processed/summary.json
- data/processed/run_info.json

The summary contains the source URL, record count, genre counts, average ratings
by language, network counts, decade counts, missing-value counts, and featured_shows.

To view the generated summary in VS Code:

```bash
code data/processed/summary.json
```

Alternatively, expand data/processed in the VS Code Explorer and click
summary.json.

## Check it

```bash
python -m pytest
python -m mypy
python -m ruff check .
python -m ruff format --check .
```

The current test suite contains 50 passing tests. The tests do not require
internet access.

## Settings

Settings are loaded with tomllib into a frozen Settings dataclass.
All six fields are required.

| Field | Meaning | Supplied value |
| --- | --- | --- |
| url | HTTP or HTTPS endpoint returning a list of show objects | https://api.tvmaze.com/shows?page=0 |
| timeout | Positive finite request timeout in seconds | 10 |
| output_folder | Non-empty output directory path | data/processed |
| seed | Integer used for repeatable sampling | 42 |
| sample_size | Non-negative number of featured shows | 5 |
| log_level | DEBUG, INFO, WARNING, ERROR, or CRITICAL | INFO |

Relative output paths are resolved from the current working directory.
If sample_size exceeds the number of records, all available shows are selected.

## Errors and exit codes

Expected application errors inherit from TVSummaryError.

| Error | When it happens | What the user sees |
| --- | --- | --- |
| SettingsError | Settings file is missing, unreadable, invalid TOML, incomplete, or contains invalid values | ERROR log and an Error: message on stderr |
| DownloadError | Connection, timeout, or HTTP request fails | ERROR log and an Error: message on stderr |
| ResponseShapeError | Response is invalid JSON or is not a list | ERROR log and an Error: message on stderr |
| ReportError | An output file cannot be written | ERROR log and an Error: message on stderr |

Successful execution returns exit code 0.
Expected application failures return exit code 1 without a traceback.
Argparse handles command-line usage errors separately and returns exit code 2.

Low-level request, parsing, and file errors are translated using exception
chaining. The entry point handles expected application errors.

A non-object item inside the response list is skipped with a WARNING.
Missing optional show fields are cleaned by Show and included in the
missing-value calculations.

To check a missing settings file:

```bash
python -m tvsummary.main --config config/missing.toml
```

In Anaconda Prompt, check the exit code immediately afterward:

```bat
echo %ERRORLEVEL%
```

The expected result is 1. In PowerShell, use $LASTEXITCODE instead.

## Logging

Each reporting module uses a named logger. Logging is configured by the entry
point through logging_setup.py.

- DEBUG records individual record processing and aggregation calculations.
- INFO records download, summary, and file-writing milestones.
- WARNING records skipped invalid items.
- ERROR records failures that stop the application.

Log messages use parameter arguments rather than formatted strings.
Record contents and request credentials are not logged.

## Reproducing a run

Use the same Python version, installed package versions, settings, and input
records in the same order.

Featured shows are selected using a local random.Random(seed) instance.
The same seed and ordered records produce the same selection without changing
the global random state.

run_info.json records all settings, the Python version, and the installed
pytest, mypy, and Ruff versions.

The live TVMaze data can change. Using the same URL and seed alone does not
guarantee identical results if the downloaded records or their order change.

## What the tests cover

The offline tests cover:

- Show cleanup for valid, missing, and malformed values.
- Every aggregation using a shared handmade fixture in conftest.py.
- Download success and translated connection, HTTP, and JSON errors.
- Invalid response shapes and warnings for skipped records.
- Required settings and invalid values using parametrized tests.
- JSON output and file errors using tmp_path.
- Repeatable sampling, empty input, and oversized samples.
- Preservation of input order and global random state during sampling.
- Featured shows and run-information output.
- Report progress logging.
- Entry-point success and expected failures, including exit codes,
  stderr messages, and ERROR logs.

Live TVMaze availability is not tested automatically because network access
would make the test suite dependent on an external service. Requests are
replaced with mocks.

## Why the modules are separate

- models.py isolates record cleanup so calculations can work with Show objects.
- sources.py isolates HTTP requests so tests can replace the network easily.
- aggregations.py keeps each calculation independent of downloading and files.
- config.py isolates settings loading and validation from application execution.
- sampling.py isolates random selection so reproducibility can be tested.
- report.py assembles results and writes JSON without controlling the program.
- errors.py provides shared application errors without coupling modules together.
- logging_setup.py keeps logging configuration in one place.
- src/tvsummary/main.py connects the responsibilities and controls exit codes.
- The root main.py delegates to the package entry point to avoid duplicate logic.

## Behaviour preservation

During the Lab 03 refactor, the original and refactored summary builders were
compared using the same downloaded records. Their dictionaries matched.

Lab 04 keeps the existing aggregation keys and calculations and adds
featured_shows when settings are supplied. The source_url reflects the configured
URL.

The original records.py remains available in Git history.

## Known limitations

- The supplied URL retrieves only TVMaze page 0; there is no automatic pagination.
- Downloading requires internet access and an available server.
- Live source updates can change the output between runs.
- Raw records are held in memory and are not saved under data/raw.
- Premiere-year extraction checks the first four characters rather than the
  entire date.
- Run commands from the repository root when using the supplied relative paths.
- Output files are written separately; if writing run_info.json fails,
  summary.json may already have been saved.
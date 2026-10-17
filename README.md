# Local Search Kit

Search local Markdown and text files offline, returning ranked excerpts with file paths and line numbers.

**Status:** runnable CLI foundation. No hosted demo or dashboard is available yet. Examples use synthetic offline data. Python 3.10+; standard library only. Validated with Python 3.12.

## Quick start

```bash
git clone https://github.com/manojPragada/local-search-kit.git
cd local-search-kit
python --version
python app.py examples "keyword source"
python app.py examples "semantic" --limit 3
```

Use `python3` if your system does not provide `python`. No package installation or API key is needed.

## Usage and behavior

Results rank by the fraction of distinct query words matched on a single line, then by path and line for deterministic ties. Matching is case-insensitive and Unicode-aware. Citations are relative file paths and one-based line numbers.

Run `python app.py --help` for available options.

## Development and verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py tests
```

Tests exercise behavior with temporary/local data. PufferFish's recording test uses only a loopback HTTP server. There is no build step or configured linter; compilation is a syntax check, not linting.

## Configuration

Configuration is provided through CLI arguments. No environment variables, `.env` file, credentials or external services are required. `.env.example` documents this intentionally empty configuration contract.

## Structure

```text
app.py          CLI and core domain functions
examples/       synthetic example inputs (queue-lab uses commands above)
tests/          behavioral unit tests
ROADMAP.md      completed work and prioritized next steps
.env.example    configuration notes
```



## Architecture

A single dependency-free module exposes importable core functions and a CLI entry point. Filesystem and network access occur only when the corresponding commands run. This small foundation will be split into a package, integrations and UI as those features arrive; see the roadmap.

## Limitations

Only UTF-8 `.txt` and `.md` files up to 1 MiB are considered. Hidden paths, symlinks and unreadable files are skipped. Queries scan files afresh; there is no index, semantic search, PDF extraction or UI yet. Use a trusted folder; this is not a sandbox against concurrent malicious filesystem changes.

## Running and deployment

Run locally from the repository using the commands above. No hosted deployment has been configured. Do not expose a development process publicly. A web deployment guide will be added when a web application actually exists.

## Troubleshooting

- **Python not found:** install Python 3.10+ or try `python3`.
- **File not found:** run from the repository root or provide an absolute input path.
- **Invalid input:** inspect the error printed to standard error and compare with the examples.
- **Permission denied:** choose a folder you own; avoid running as administrator.

## Contributing and credits

Open an issue describing the observed behavior, expected result and a minimal synthetic example. Keep changes focused, include behavioral tests, run the checks above, and update this README when commands or capabilities change. Do not submit credentials or private input files.

Implementation and synthetic examples are original to this repository. There are no third-party runtime dependencies or media assets. A redistribution license has not yet been selected; public visibility alone does not grant an open-source license.

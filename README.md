# Local Search Kit

Search local Markdown and text files offline, returning ranked excerpts with file paths and line numbers.

**Status:** runnable CLI plus standalone local results UI. No hosted demo is available. Examples use synthetic offline data. Python 3.10+; standard library only. Validated with Python 3.12.

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

Benchmark JSON now includes bounded per-case rank and candidate-count diagnostics alongside aggregate top-1 accuracy and mean reciprocal rank, making regressions inspectable without changing ranking behavior.

Results rank by the fraction of distinct query words matched on a single line, then by path and line for deterministic ties. Matching is case-insensitive and Unicode-aware. Citations are relative file paths and one-based line numbers.

Run `python app.py --help` for available options.

### Optional local reranker protocol

`--reranker /absolute/path/to/executable` sends a versioned JSON object containing the query and already-selected candidate excerpts plus lexical scores to a local executable over standard input. The executable must return a JSON array with one finite score from 0 to 1 per candidate within ten seconds. Scores only reorder the existing lexical results: the adapter does not provide file paths or line numbers to the model, so it cannot invent citations. A rerank score is model-specific ordering metadata, not confidence or relevance truth.

The executable is code you choose to run with your own permissions. No reranker is bundled, downloaded or contacted by default; validate and sandbox third-party models yourself.

Evaluate a candidate local model against a small, human-labelled JSON set before trusting its ordering:

```bash
python benchmark.py examples/benchmark.json /absolute/path/to/reranker
```

Each case supplies a query, 1–100 candidate strings and the zero-based index of the relevant candidate. The harness reports top-1 accuracy and mean reciprocal rank. The bundled two-case set is only a protocol smoke test, not evidence of model quality; replace it with representative private cases and do not commit sensitive text.

`examples/tfidf_reranker.py` is a dependency-free local statistical baseline implementing the protocol. It scores only query-word overlap using TF-IDF; it is not an embedding model, does not understand meaning and cannot retrieve candidates missed by lexical search. Run it reproducibly with:

```bash
chmod +x examples/tfidf_reranker.py
python benchmark.py examples/benchmark.json ./examples/tfidf_reranker.py
```

On the bundled two-case smoke set this baseline produces top-1 accuracy `0.5` and mean reciprocal rank `0.75`. Those two synthetic cases are far too small for a quality claim; the numbers exist only to make the example reproducible and comparable with future adapters.

Use `--context 0..5` to include neighboring source lines around each citation in JSON, Markdown and HTML output. The exact matching line is marked separately in context views; ranking and citation line numbers do not change. Context is read locally after matching and is never sent elsewhere.

```bash
python app.py examples "keyword source" --context 2 --format html --output search-report.html
```

## Persistent incremental index

```bash
python app.py examples "keyword source" --index /tmp/local-search-demo.sqlite3
```

Use a writable database path with an existing parent folder. Each indexed search scans eligible files and computes content hashes, then retokenizes only added or changed files. Deleted or newly excluded/unreadable documents are removed. This avoids repeating tokenization, but still reads and hashes source files; it is not a filesystem watcher or a full-text SQL index. Query matching scans stored tokenized lines with the same ranking and citations as ordinary search.

Each database is bound to one resolved root folder. Choose a new database when searching another folder. The index contains document excerpts and tokens: keep it private, and delete it when no longer needed. Database files are ignored by git. Only use index files you trust.

## Readable search reports

```bash
python app.py examples "keyword source" --format markdown
python app.py examples "keyword source" --index /tmp/local-search-demo.sqlite3 --format markdown
```

JSON remains the default. Markdown output includes the query, ranked matches, relative file/line citations, excerpts and query-word coverage percentages. Percentages are lexical match coverage, not semantic confidence. Source paths and document text are formatted as literal code. Reports may contain private document excerpts: review before sharing.

For a responsive local results interface with clickable citations:

```bash
python app.py examples "keyword source" --format html --output search-report.html
```

Open `search-report.html` in a browser. The report contains no external requests and is created exclusively rather than overwriting a file. Citations use local `file:` URLs with a conventional `#L` fragment; opening and line scrolling depend on browser/OS support. The report embeds excerpts and absolute local file URLs, so keep it private. HTML files are not indexed by this tool.

## Development and verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py benchmark.py reporting.py reranker.py web_report.py examples/tfidf_reranker.py tests
```

Tests exercise temporary documents and SQLite indexes, including updates, deletions, root binding and unchanged-file reuse. There is no build step or configured linter; compilation is a syntax check, not linting.

## Configuration

Configuration is provided through CLI arguments. No environment variables, `.env` file, credentials or external services are required. `.env.example` documents this intentionally empty configuration contract.

## Structure

```text
app.py          CLI and search/index logic
reporting.py    literal-text Markdown result reports
reranker.py     bounded optional local executable adapter
benchmark.py    bounded offline reranker evaluation harness
web_report.py   standalone responsive HTML result renderer
examples/       synthetic example inputs
tests/          behavioral unit tests
ROADMAP.md      completed work and prioritized next steps
.env.example    configuration notes
```



## Architecture

### Match every query word

```bash
python app.py examples 'local search' --match all
python app.py examples 'local search' --match all --index search.sqlite3 --format markdown
```

`--match any` preserves the default ranking. `--match all` requires every distinct case-folded query word on the **same line**, not merely somewhere in a document. Word order and duplicates do not matter; this is not exact phrase, fuzzy or semantic search. All-mode results have lexical coverage 1.0, not a confidence probability. Direct and indexed searches share the matching rule and deterministic source/line tie-breaks; switching modes does not require an index rebuild. Imported Python callers can pass `match='all'`; limits must be positive integers. Empty/punctuation-only queries and unknown modes are errors.

A single dependency-free module exposes importable core functions and a CLI entry point. Filesystem and network access occur only when the corresponding commands run. This small foundation will be split into a package, integrations and UI as those features arrive; see the roadmap.

## Limitations

Only UTF-8 `.txt` and `.md` files up to 1 MiB are considered. Hidden paths, symlinks and unreadable files are skipped. The default mode scans files afresh; optional indexed mode persists tokenized lines. There is no semantic search or PDF extraction. Use a trusted folder; this is not a sandbox against concurrent malicious filesystem changes.

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




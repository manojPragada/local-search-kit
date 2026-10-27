# Roadmap

## Completed

- [x] Runnable standard-library CLI foundation
- [x] Behavioral tests and documented local examples
- [x] Input handling, explicit limitations and setup guide

## Next

- [x] Add persistent index with incremental file updates
- [x] Add readable Markdown result reports with line citations
- [x] Build local results UI with clickable source citations
- [x] Define bounded local reranker adapter contract
- [x] Add a reproducible local statistical reranker baseline
- [ ] Add an optional embedding example only with measured benefit over the baseline

## Continuity

2026-10-27: Added bounded per-case rank diagnostics to benchmark output so regressions are inspectable instead of hidden behind aggregate top-1/MRR values. Next: measure any optional embedding example against the same labelled cases.

2026-10-26: Added a dependency-free TF-IDF reranker executable and testable benchmark command. It is explicitly a lexical statistical baseline, not semantic search. Next: consider an optional embedding example only after measuring improvement on representative labelled cases.

2026-10-25: Added a bounded offline reranker evaluation harness with top-1 accuracy and mean reciprocal rank plus a clearly labelled two-case protocol smoke test. Next: document a reproducible local embedding model result without making general quality claims.

2026-10-24: Added an opt-in local executable reranker protocol. It receives only query/excerpt/lexical-score candidates, must return one bounded score per input, times out after 10 seconds and can reorder but never invent citations. Next: a benchmarked local-model example kept separate from default lexical ranking.

2026-10-22: Added bounded 0–5-line source context across direct/indexed JSON, Markdown and HTML results, with the cited line visibly distinguished and escaped. Next: define a stable optional local-model adapter contract without making semantic claims about lexical results.

2026-10-21: Added a responsive standalone HTML results UI with literal excerpts, lexical coverage labels, visible empty state and clickable file/line citations. Output uses exclusive creation and makes no network requests. Next: optional embeddings and clearly separated local model adapters.

2026-10-20: Added --match all for same-line conjunction of distinct query words, preserving default any-word ranking. Shared direct/indexed matching and stricter argument validation; seven tests cover Unicode, duplicates, parity, refresh and CLI JSON/Markdown. Next: local source-citation UI; no semantic search or dashboard claimed.

Initial foundation implemented and checked on 2026-10-17. Inspect current code and commits before continuing. Prioritize the first unchecked item and keep improvements small enough to verify. No visual dashboard has been implemented.


2026-10-18: Added optional root-bound SQLite index, content-hash reuse and stale-document cleanup. Nine tests pass. Next: local results UI with source citations; browser review will be required before claiming visual completion.


2026-10-19: Added --format markdown for direct and indexed search, with literal excerpts and explicit lexical coverage labels. JSON remains the default. Web UI and clickable local citations remain pending.


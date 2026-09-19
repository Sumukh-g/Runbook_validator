# Completion baseline

Recorded before the completion/hardening work on 2026-09-19 UTC.

## Repository state

- Baseline commit: `1a96f28` (`Build OpsProof explainable runbook assurance engine`).
- Branch: `work`.
- Working tree: clean.
- Compilation: `python -m compileall -q opsproof evaluation app.py` passed.
- Tests: `pytest -q` reported **12 passed, 1 skipped**. The skipped test was the optional DOCX test because `python-docx` was unavailable.
- Controlled mutation benchmark: **7/7 detected (100.0%)**. This is a small controlled robustness suite, not real-world accuracy.

## Implemented at baseline

- TXT/Markdown ingestion, optional DOCX extraction, source references, and typed dataclass OIR.
- Thirty-four generic rules and five domain policy packs loaded from JSON-compatible YAML files.
- Deterministic rule evaluation, lexical SQL/shell analysis, serialized procedure graph, and three Python safety invariants.
- Logical failure-mode coverage, static risk, deterministic assurance scoring, greedy remediation, JSON/Markdown exports.
- Parameterized SQLite history with filename-based version comparison.
- Streamlit source implementation, weak/improved examples, seven mutation operators, documentation, and non-execution tests.

## Incomplete or unvalidated at baseline

- Runtime dependencies were unavailable in the container: Pydantic, PyYAML, python-docx, NetworkX, sqlglot, bashlex, z3-solver, SQLAlchemy, Streamlit, pandas, NumPy, scikit-learn, Plotly, RapidFuzz, ReportLab, and pytest-cov.
- Production Pydantic `BaseModel` validation, true safe YAML parsing, AST-backed SQL/shell parsing, NetworkX graph algorithms, Z3 cross-checking, constrained remediation, local semantic backend, calibration experiment, PDF export, and UI runtime tests were absent.
- Mutation coverage was limited to seven operators; no 25-document annotated cross-domain benchmark or rigorous multi-stage ablation existed.
- The existing graph was a serialized dictionary rather than a NetworkX graph, and the evaluator was centralized.

This file is intentionally historical. Final capabilities and remaining limitations are tracked separately in `implementation_status.md` and `test_results.md`.

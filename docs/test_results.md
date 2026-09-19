# Test and evaluation results

Generated from actual commands on 2026-09-19 UTC. Results are environment-specific and must be regenerated after material changes.

## Automated tests

- `pytest -q`: **33 passed, 2 skipped** at the time this report was generated. Skips: optional DOCX test (`python-docx` unavailable) and Streamlit AppTest (`streamlit` unavailable).
- `python -m compileall -q opsproof evaluation app.py`: passed.
- `ruff check .`: passed under the repository configuration. Legacy compact one-line formatting checks E701/E702 are excluded; correctness/unused-import checks remain active.

## Controlled mutation robustness

`python -m evaluation.benchmark --json` executed 26 deterministic mutations and detected **26/26 (100.0%)**. This measures known injected defects, not real-world accuracy.

## Controlled cross-domain benchmark

`python -m evaluation.controlled_benchmark` evaluated 25 internally annotated documents across database, Linux service, application deployment, Kubernetes, and incident response:

- TP: 60
- FP: 80
- FN: 0
- Precision: 0.429
- Recall: 1.000
- F1: 0.600

The low precision is reported without adjustment. Labels are controlled project annotations with no independent expert review, and the intentionally narrow expected-rule sets classify additional plausible findings as false positives.

## Ablation

| Model | Precision | Recall | F1 | Avg findings |
|---|---:|---:|---:|---:|
| A — keyword/checklist families | 0.429 | 0.500 | 0.462 | 2.8 |
| B — structured rules | 0.304 | 0.583 | 0.400 | 4.6 |
| C — OIR + command analysis | 0.407 | 0.917 | 0.564 | 5.4 |
| D — graph reasoning | 0.429 | 1.000 | 0.600 | 5.6 |
| E — full deterministic result | 0.429 | 1.000 | 0.600 | 5.6 |

Graph reasoning recovers the annotated sequencing defects. Model B's precision is worse on this controlled set; this is retained rather than hidden.

## Performance sample

Measured with Python 3.14.4 in this container, excluding optional semantic loading:

| Case | Bytes | Steps | Latency | Peak traced memory |
|---|---:|---:|---:|---:|
| Small | 78 | 1 | 9.516 ms | 200.3 KiB |
| Medium | 3,992 | 100 | 32.309 ms | 376.9 KiB |
| Large | 41,793 | 1,000 | 356.170 ms | 3,591.8 KiB |

These are observations, not performance gates.

## Environment limitations

`pytest-cov` was unavailable, so the requested coverage command could not run and no coverage percentage is claimed. Pydantic, PyYAML, python-docx, NetworkX, sqlglot, bashlex, z3-solver, Streamlit, ReportLab, scikit-learn, NumPy, and pytest-cov were unavailable. Tested deterministic fallbacks remained active. Full dependency-path, coverage, Z3, NetworkX, parser-AST, DOCX, PDF-via-ReportLab, calibration, and UI runtime validation must run in CI or an environment where declared dependencies can be installed.

A local installation attempt with `python -m pip install -e '.[dev]' --no-build-isolation` could not start because this container lacks the `setuptools.build_meta` backend and cannot fetch dependencies. This is an environment limitation, not a passing dependency-path validation.

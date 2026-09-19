# Testing and evidence

The suite covers ingestion boundaries and sources, optional DOCX, OIR, policy schema and hostile YAML, SQL/shell analysis, graph ordering, formal invariants, resource-linked failure coverage, risk, scoring pathology/order independence, greedy/constrained remediation, SQLite regression deltas, JSON/Markdown/PDF reports, semantic fallback, 26 mutation operators, hostile command non-execution, and optional Streamlit AppTest.

Run:

```bash
pytest -q
pytest --cov=opsproof --cov=evaluation --cov-report=term-missing
ruff check .
python -m compileall -q opsproof evaluation app.py
python -m evaluation.benchmark --json
python -m evaluation.controlled_benchmark
python -m evaluation.ablation
python -m evaluation.performance
```

No benchmark result is hard-coded into the analyser. See `test_results.md` for recorded output and explicit dependency limitations.

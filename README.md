# OpsProof

**Explainable Runbook Quality and Safety Assurance Engine** — a local-first compiler-style static analyser for operational runbooks. OpsProof accepts TXT, Markdown, and DOCX, builds a typed Operational Intermediate Representation (OIR), and produces evidence-linked findings, assurance scoring, risk, failure coverage, remediation, and version regression analysis. **Runbook commands are untrusted text and are never executed.**

## Why OpsProof is not a keyword checker

A checklist sees the word **backup** and passes. OpsProof models the procedure:

```text
EXPECTED: verified backup → DELETE production records
ACTUAL:   DELETE production records → verify backup
RESULT:   critical sequencing finding with both source steps
```

That conclusion is produced through the same canonical OIR, command parser, procedure graph, deterministic `SEQ-001` rule, and formal `INV-A` invariant. It is not special-cased to a sample filename. The system also links verification/recovery to risky actions, models logical failure modes, exposes risk factors and score deductions, optimises remediation, and measures controlled mutations.

## Architecture

```text
Untrusted TXT/MD/DOCX → bounded ingestion → typed OIR
 → safe YAML policies + SQL/shell static parsers
 → NetworkX graph → Python invariants + optional Z3 cross-check
 → resource-linked failure coverage → risk + transparent score
 → greedy/constrained remediation → SQLite + JSON/Markdown/PDF/UI
```

Optional dependencies have conservative offline fallbacks. Optional local semantic assistance only proposes candidate signals; it cannot decide findings, severity, safety classification, or scores. See [architecture](docs/architecture.md), [methodology](docs/methodology.md), and [Responsible AI](docs/responsible_ai.md).

## Install and run

Requires Python 3.11+.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
streamlit run app.py
```

No API keys, telemetry, cloud database, paid inference, or internet connection are required at runtime. Environment options are documented in `.env.example`.

## Tests and measured evaluation

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

The repository contains 26 mutation operators and 25 controlled cross-domain documents. Labels are internal project annotations—not independent expert review. Actual recorded results and environment constraints are in [test results](docs/test_results.md).

## Inputs and policy packs

Inputs are UTF-8 `.txt`, `.md`, `.markdown`, and non-macro `.docx`, bounded to 5 MiB by default. Packs are `generic` (always active), `database`, `linux`, `deployment`, `kubernetes`, and `incident_response`. Policies use safe YAML, a strict key/schema allow-list, typed metadata, and a fixed evaluator registry; they cannot contain executable configuration.

## Scoring and explainability

Each category starts at 100. Unique rule/location penalties are deducted up to a 60-point category cap, then documented category weights form the overall score. Finding order cannot change the result. Every finding exposes what, where, why, rule, severity, evidence, remediation, detector, confidence, and score impact. Say “92/100 under the configured validation policy,” never “92% safe.”

## Security and privacy

Uploads remain local. There is no shell, SQL connection, execution adapter, or network inference dependency. Tests patch `os.system`, six subprocess APIs, and analyse substitution, chaining, redirection, SQL, Python-like, and PowerShell-like hostile content while asserting zero execution. See [security](docs/security.md).

## Competition demo

1. Select the database pack and upload `examples/weak/weak_database_runbook.md`.
2. Inspect exact evidence, deductions, failure gaps, and remediation.
3. Upload `examples/edge_cases/high_risk_commands.md` to demonstrate static-only SQL/shell parsing.
4. Upload `examples/weak/database_backup_after_delete.md`; show the **Critical Risk Path**, red invalid graph edge, `SEQ-001`, and `INV-A`.
5. Upload `examples/improved/improved_database_runbook.md`; show fewer findings and regression deltas.
6. Run the 26-operator mutation evaluation and controlled benchmark.

Use the timed [demo script](docs/demo_script.md).

## Honest limitations

Static analysis cannot observe infrastructure and policy conformance is not proof of safety. Parser fallbacks do not emulate runtime expansion. Resource linking is conservative. The benchmark is controlled and internally annotated. Scores and remediation gains are policy-relative estimates. Authentication and multi-user SaaS concerns are out of scope. See [limitations](docs/limitations.md) and [implementation status](docs/implementation_status.md).

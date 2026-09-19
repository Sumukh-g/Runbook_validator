# Implementation status

| Module | Status | Evidence / qualification |
|---|---|---|
| TXT/Markdown ingestion and OIR | TESTED | Boundary, source, integration tests |
| DOCX paragraphs/tables | IMPLEMENTED | Test exists; skipped locally because dependency unavailable |
| Typed production models | IMPLEMENTED | Pydantic dataclasses when installed; tested stdlib fallback, full BaseModel migration remains future work |
| Safe YAML policies + schema validation | TESTED | `safe_load` production path; hostile/invalid policy tests; JSON subset fallback tested offline |
| 34 generic rules + five domain packs | TESTED | Loader and regression tests |
| SQLglot SQL parser + lexical fallback | IMPLEMENTED | Fallback tested locally; SQLglot path dependency-blocked |
| bashlex shell AST + shlex fallback | IMPLEMENTED | Fallback tested locally; bashlex path dependency-blocked |
| NetworkX MultiDiGraph + offline graph fallback | IMPLEMENTED | Algorithms/fallback tested; NetworkX path dependency-blocked |
| Python safety invariants INV-A/B/C/D/F | TESTED | Ordering regression and engine tests |
| Z3 consistency cross-check | IMPLEMENTED | Optional production path; dependency-blocked locally |
| Resource-linked failure analysis | TESTED | Engine tests |
| Expanded transparent risk model | TESTED | Integration tests |
| Order-independent capped scoring | TESTED | Pathology and determinism tests |
| Greedy + exact budget optimiser | TESTED | Unit tests; Z3 Optimize not required for small sets |
| SQLite logical identity/regression deltas | TESTED | Parameterized temporary database tests |
| JSON/Markdown/PDF export | TESTED | Pure-PDF fallback tested; ReportLab path dependency-blocked |
| Optional local semantic backends | TESTED | Disabled/fallback tested; local model optional and not downloaded |
| BayesianRidge calibration experiment | EXPERIMENTAL | Disabled without 30 legitimate labels and sklearn; empty schema supplied |
| 26-operator mutation evaluation | TESTED | 26/26 detected in recorded run |
| 25-document controlled benchmark | TESTED | Metrics generated; no independent expert review |
| Five-stage controlled ablation | TESTED | Actual measured results documented |
| Performance benchmark | TESTED | Small/medium/large observations documented |
| Streamlit UI | IMPLEMENTED | AppTest exists; runtime blocked locally by unavailable dependency |
| CI workflow | IMPLEMENTED | Installs full deterministic dependencies; not executed in local container |

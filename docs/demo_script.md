# Competition demo script — 7 minutes

## 00:00 — Positioning

“OpsProof is static assurance for operational runbooks: a compiler, linter, graph reasoner, and safety auditor. It runs locally, needs no cloud LLM, and never executes runbook commands.”

## 00:30 — Weak runbook

Launch `streamlit run app.py`, select **database**, and upload `examples/weak/weak_database_runbook.md`. Show the assurance score, risk, severity counts, category scores, and active policy pack. Emphasize that the number is policy-relative—not a probability.

## 01:15 — Explainable evidence

Open Findings. Expand missing prerequisites, vague verification, absent rollback, and unprotected production mutation. Point out exact evidence/source, rule, rationale, detector, remediation, confidence, and deduction.

## 02:00 — Dangerous text, zero execution

Upload `examples/edge_cases/high_risk_commands.md`. Show SQL DELETE-without-WHERE and recursive/wildcard/privileged shell findings. State that SQLglot/bashlex parse ASTs when installed; no shell or database connection exists. The security suite patches six subprocess APIs.

## 02:40 — The ten-second “wow” moment

Upload `examples/weak/database_backup_after_delete.md`. Pause on **CRITICAL RISK PATH**:

```text
EXPECTED: verified backup → delete
ACTUAL:   delete → backup verification
```

Say: “A keyword checker sees backup and passes. OpsProof proves the safeguard exists too late.”

## 03:20 — Graph and formal evidence

Open Procedure Graph. Show the red invalid `PROTECTS` edge and distinct action/safeguard/verification/recovery nodes. Open Failure Analysis and show deterministic `SEQ-001`, invariant `INV-A`, and uncovered document-level failure modes.

## 04:15 — Minimal remediation

Open Remediation. Show ranked gain, risk reduction, effort, and estimated assurance. Explain that the exact budget optimiser selects a deterministic high-value subset and never rewrites commands.

## 05:00 — Improved runbook

Upload `examples/improved/improved_database_runbook.md`. Highlight owner, purpose, bounded scope, prerequisites, approval, verified snapshot before mutation, constrained SQL, measurable verification, rollback trigger, and escalation.

## 05:45 — Version regression

Analyse weak and improved content under one logical runbook name. Show score/category/failure-coverage deltas, resolved/introduced/unchanged findings, and risk-path changes.

## 06:20 — Measured evaluation

Run `python -m evaluation.benchmark --json`: 26 controlled mutations are generated and analysed. Show `python -m evaluation.controlled_benchmark` and the honest precision/recall/F1 results; explicitly state labels are internal, not independent expert validation. Show ablation evidence that graph reasoning recovers ordering defects.

## 06:55 — Close

“No cloud LLM, no command execution, deterministic safety rules, optional local semantic candidate assistance only. Static policy conformance is useful evidence—not proof of safety.”

Reset by deleting `opsproof.db` or setting `OPSPROOF_DB_PATH` to a fresh local file.

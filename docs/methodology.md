# Hybrid assurance methodology

OpsProof treats a runbook as a source program rather than a bag of words. One canonical OIR feeds several independent, explainable analyses:

1. deterministic rules define auditable acceptance criteria;
2. SQL/shell AST parsers (with conservative fallbacks) identify structural command risk without execution;
3. graph relationships reason about safeguards, actions, verification, recovery, resources, and order;
4. explicit Python invariants and an optional Z3 consistency check verify finite temporal constraints;
5. resource-linked failure-mode analysis asks how success, complete/partial failure, verification failure, and rollback failure are covered;
6. a documented factor model estimates policy-relative static risk;
7. capped, order-independent scoring exposes every deduction;
8. deterministic optimisation ranks the smallest high-value remediation set; and
9. controlled mutations, annotations, ablation, and performance scripts measure the implementation rather than hard-coding claims.

## Why not an end-to-end LLM?

A large hosted model would weaken repeatability, introduce token cost and data transmission, complicate auditability, and make acceptance decisions difficult to reproduce. OpsProof therefore works offline on small hardware. An optional already-local sentence-transformer may propose similarity candidates, but deterministic logic alone owns findings, severity, safety classification, scoring, and tests.

A finding uses qualified language such as “potentially destructive” and includes what, where, rule, severity, evidence, rationale, remediation, detector, confidence, and score impact. The system never predicts actual infrastructure behaviour.

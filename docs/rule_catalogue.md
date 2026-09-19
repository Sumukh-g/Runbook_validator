# Rule catalogue

`policies/generic.yaml` defines 34 baseline rules across completeness (COMP), ownership (OWN), escalation (ESC), verification (VER), recoverability (REC), clarity (CLR), sequencing (SEQ), safety (SAFE), and command safety (CMD). Domain packs add DB, LINUX, DEP, K8S, and IR rules. Each record provides ID, category, description, rationale, severity, enabled flag, evaluator, penalty, remediation, and optional parameters.

Notable structural rules include SQL DELETE/UPDATE without WHERE, recursive forced deletion, wildcard scope, privileged/cluster scope, safeguard-after-action, high-risk action without later verification, non-actionable rollback, and production mutation without prior approval.

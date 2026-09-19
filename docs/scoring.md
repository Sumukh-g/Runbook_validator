# Deterministic scoring

Each category begins at 100. For every unique `(rule ID, source step)` finding, the configured non-negative penalty is deducted. Total deduction in a category is capped at 60 so repeated low-level findings cannot erase that category. Scores therefore remain 40–100 in the current baseline.

Overall score is the weighted sum: completeness 14%, safety 18%, recoverability 14%, verification 14%, clarity 10%, sequencing 12%, ownership 7%, escalation 5%, command safety 4%, operational logic 2%. Every applied deduction is included in `ScoreReport.contributions`.

The value is an assurance score under selected policies, not a probability, certification, or proof of safety. Estimated remediation gains are bounded heuristics and require re-analysis after edits.

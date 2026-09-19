# Known limitations

- Static analysis cannot understand every operational context or observe live infrastructure state; policy conformance is not proof of safety.
- Referenced external procedures are unavailable unless their relevant controls are embedded in the runbook.
- Command parsers do not emulate execution. Shell expansion, aliases, environment variables, permissions, and runtime effects remain unknown.
- Optional AST, graph, solver, DOCX, PDF, calibration, and UI paths require their declared dependencies; deterministic fallbacks preserve offline analysis when unavailable.
- Semantic NLP is optional, local-only, and non-authoritative. The deterministic fallback is lexical similarity, not language understanding.
- The controlled benchmark is internally annotated and has no independent expert review. Its metrics are not industrial or real-world accuracy claims.
- OIR resource linking is conservative and may produce false positives or false negatives, particularly when steps use aliases or external references.
- DOCX evidence uses paragraph/table coordinates, not rendered line numbers; macros and embedded objects are ignored.
- Assurance score and remediation impact are policy-relative estimates, not incident probabilities or guarantees.
- The PDF fallback is intentionally plain. ReportLab produces the richer production export when installed.
- Stable logical identity is supported, with filename fallback. Authentication, authorization, and multi-user isolation are outside this local competition application's scope.

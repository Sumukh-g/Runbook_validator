# Security and privacy

Uploads are hostile data. OpsProof strips paths to a basename, allow-lists four extensions, enforces a configurable size bound, rejects NUL/bad UTF-8, does not extract archives, and reads DOCX text without invoking macros or embedded objects. Policies use `yaml.safe_load`, allowed keys, typed metadata, and fixed evaluator identifiers—never unsafe constructors, dynamic imports, or code.

The analysis domain has no execution adapter. Runbook strings never reach `eval`, `exec`, a shell, subprocess, SQL connection, or template evaluator. Tests patch `os.system`, `subprocess.run`, `Popen`, `call`, `check_call`, and `check_output` while analysing command substitution, backticks, chaining, redirection, SQL, Python-like, PowerShell-like, and malformed shell text. Evidence is displayed with Streamlit text/code widgets; the only `unsafe_allow_html` content is a constant application-owned banner/panel.

Data remains local. Logs contain filename, byte count, selected policies, duration, rule count, finding count, and errors—but never full uploaded content by default. There is no telemetry or external inference call.

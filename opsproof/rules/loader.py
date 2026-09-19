from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from opsproof.core.config import POLICY_DIR
from opsproof.core.enums import Category, Severity
from opsproof.core.exceptions import PolicyError
from opsproof.core.models import RuleDefinition
from .registry import EVALUATOR_IDS

_ALLOWED_PACK_KEYS={"name","version","rules"}
_ALLOWED_RULE_KEYS={"id","name","category","description","rationale","severity","enabled","evaluator","score_penalty","remediation","parameters"}

def _safe_load(text: str) -> Any:
    """Use PyYAML safe_load in production; JSON fallback supports the bundled YAML subset offline."""
    try:
        import yaml
    except ImportError:
        try: return json.loads(text)
        except json.JSONDecodeError as exc: raise PolicyError("PyYAML is unavailable and the policy is not JSON-compatible YAML.") from exc
    try: return yaml.safe_load(text)
    except yaml.YAMLError as exc: raise PolicyError("Malformed or unsafe YAML policy.") from exc

class PolicyLoader:
    def __init__(self, directory: Path = POLICY_DIR): self.directory=directory
    def load(self, packs: list[str] | None = None) -> list[RuleDefinition]:
        names=["generic",*(p for p in (packs or []) if p != "generic")]; rules=[]; ids=set()
        for name in names:
            if not name or not name.replace("_","").isalnum(): raise PolicyError("Invalid policy pack name.")
            path=self.directory/f"{name}.yaml"
            if not path.is_file(): raise PolicyError(f"Unknown policy pack: {name}")
            data=_safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data,dict) or set(data)-_ALLOWED_PACK_KEYS or not isinstance(data.get("rules"),list): raise PolicyError(f"Policy pack {name} has an invalid structure.")
            for raw in data["rules"]:
                if not isinstance(raw,dict) or set(raw)-_ALLOWED_RULE_KEYS: raise PolicyError(f"Policy pack {name} contains unsupported configuration.")
                rid=raw.get("id")
                if not isinstance(rid,str) or not rid.strip(): raise PolicyError(f"Policy pack {name} has a rule without an ID.")
                if rid in ids: raise PolicyError(f"Duplicate rule ID: {rid}")
                if raw.get("evaluator") not in EVALUATOR_IDS: raise PolicyError(f"Rule {rid} references an unknown evaluator.")
                try:
                    penalty=float(raw["score_penalty"])
                    if not 0 <= penalty <= 100: raise ValueError
                    cooked={**raw,"score_penalty":penalty,"category":Category(raw["category"]),"severity":Severity(raw["severity"])}
                    rule=RuleDefinition.model_validate(cooked)
                except (KeyError,ValueError,TypeError) as exc: raise PolicyError(f"Rule {rid} has invalid typed metadata.") from exc
                if rule.enabled: rules.append(rule)
                ids.add(rid)
        return rules

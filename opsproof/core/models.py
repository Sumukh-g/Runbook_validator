from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .enums import Category, Severity
from dataclasses import dataclass as std_dataclass, field, asdict
try:
    from pydantic.dataclasses import dataclass as model_dataclass
except ImportError:  # Minimal offline runtime; production requirements install Pydantic.
    model_dataclass = std_dataclass

class BaseModel:
    def model_dump(self, mode=None): return asdict(self)
    def model_dump_json(self, indent=None):
        import json
        return json.dumps(asdict(self), indent=indent, default=str)
    @classmethod
    def model_validate(cls, value): return cls(**value)

def Field(*, default_factory=None, default=None, **kwargs):
    return field(default_factory=default_factory) if default_factory is not None else field(default=default)
@model_dataclass(kw_only=True)
class SourceRef(BaseModel):
    file_name: str
    line_number: int | None = None
    paragraph_number: int | None = None
    section: str | None = None
    step_number: int | None = None
    evidence_text: str = ""

@model_dataclass(kw_only=True)
class Command(BaseModel):
    language: str
    raw_text: str
    operation: str | None = None
    target: str | None = None
    flags: list[str] = Field(default_factory=list)
    destructive: bool = False
    reversible: bool = True
    parsed_metadata: dict[str, Any] = Field(default_factory=dict)

@model_dataclass(kw_only=True)
class Step(BaseModel):
    id: str
    ordinal: int
    text: str
    normalized_text: str
    section: str
    source_ref: SourceRef
    action_verb: str | None = None
    target: str | None = None
    environment: str | None = None
    command: Command | None = None
    risk_tags: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    verification_targets: list[str] = Field(default_factory=list)
    recovery_targets: list[str] = Field(default_factory=list)

@model_dataclass(kw_only=True)
class Section(BaseModel):
    name: str
    kind: str
    source_ref: SourceRef
    content: list[str] = Field(default_factory=list)

@model_dataclass(kw_only=True)
class RunbookDocument(BaseModel):
    id: str
    file_name: str
    title: str | None = None
    purpose: str | None = None
    scope: str | None = None
    owner: str | None = None
    prerequisites: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)
    verification_steps: list[str] = Field(default_factory=list)
    rollback_steps: list[str] = Field(default_factory=list)
    escalation: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

@model_dataclass(kw_only=True)
class RuleDefinition(BaseModel):
    id: str
    name: str
    category: Category
    description: str
    rationale: str = ""
    severity: Severity
    enabled: bool = True
    evaluator: str
    score_penalty: float = Field(ge=0, le=100)
    remediation: str
    parameters: dict[str, Any] = Field(default_factory=dict)

@model_dataclass(kw_only=True)
class Finding(BaseModel):
    id: str
    rule_id: str
    category: Category
    severity: Severity
    title: str
    explanation: str
    evidence: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    remediation: str
    confidence: str = "high"
    score_impact: float
    detector: str
    metadata: dict[str, Any] = Field(default_factory=dict)

@model_dataclass(kw_only=True)
class ScoreContribution(BaseModel):
    rule_id: str
    category: Category
    deduction: float

@model_dataclass(kw_only=True)
class ScoreReport(BaseModel):
    overall: float
    categories: dict[str, float]
    contributions: list[ScoreContribution]

@model_dataclass(kw_only=True)
class FailureCoverage(BaseModel):
    step_id: str
    covered: list[str]
    uncovered: list[str]
    percentage: float
    confidence: str = "medium"
    notes: list[str] = Field(default_factory=list)

@model_dataclass(kw_only=True)
class RiskAssessment(BaseModel):
    score: float
    level: str
    factors: dict[str, float]
    statement: str
    rationale: list[str] = Field(default_factory=list)

@model_dataclass(kw_only=True)
class RemediationItem(BaseModel):
    rank: int
    recommendation: str
    fixes_rules: list[str]
    estimated_gain: float
    effort: str
    category: str
    id: str = ""
    affected_finding_ids: list[str] = Field(default_factory=list)
    risk_reduction: float = 0.0
    effort_cost: int = 1
    dependencies: list[str] = Field(default_factory=list)
    estimated_assurance: float | None = None
    estimate_label: str = "Estimated under configured policy."

@model_dataclass(kw_only=True)
class AnalysisResult(BaseModel):
    document: RunbookDocument
    findings: list[Finding]
    score: ScoreReport
    risk: RiskAssessment
    failure_coverage: list[FailureCoverage]
    remediation: list[RemediationItem]
    policy_packs: list[str]
    graph: dict[str, Any]
    analysed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    non_execution_statement: str = "Runbook commands were treated only as untrusted text and never executed."

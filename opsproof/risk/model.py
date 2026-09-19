"""Transparent policy-relative static risk model."""
from __future__ import annotations
from opsproof.core.models import FailureCoverage, Finding, RiskAssessment, RunbookDocument

def assess_risk(doc: RunbookDocument, findings: list[Finding], coverage: list[FailureCoverage] | None=None) -> RiskAssessment:
    commands=[s.command for s in doc.steps if s.command]; destructive=sum("destructive" in s.risk_tags or bool(s.command and s.command.destructive) for s in doc.steps); production=any(s.environment=="production" for s in doc.steps); irreversible=sum(not c.reversible for c in commands); privileged=sum(bool(c.parsed_metadata.get("privileged")) for c in commands); broad=sum(bool(c.parsed_metadata.get("whole_table_scope") or c.parsed_metadata.get("wildcard") or c.parsed_metadata.get("cluster_scope")) for c in commands)
    ids={f.rule_id for f in findings}; failure_gap=0 if not coverage else 1-sum(x.percentage for x in coverage)/(100*len(coverage))
    factors={"impact":min(5.0,1+1.5*destructive),"scope":min(5.0,1+2*broad),"environment":4.0 if production else 1.0,"privilege":min(5.0,1+2*privileged),"irreversibility":min(5.0,1+2*irreversible),"missing_safeguards":5.0 if ids&{"SAFE-002","SEQ-001","DB-001"} else 1.0,"verification_gap":4.0 if ids&{"VER-001","VER-004"} else 1.0,"recovery_gap":4.0 if ids&{"REC-001","REC-003","SAFE-005"} else 1.0,"failure_mode_gap":round(1+4*failure_gap,2)}
    weights={"impact":.18,"scope":.12,"environment":.12,"privilege":.08,"irreversibility":.12,"missing_safeguards":.14,"verification_gap":.09,"recovery_gap":.09,"failure_mode_gap":.06}
    score=round(sum(factors[k]/5*100*w for k,w in weights.items()),1); level="critical" if score>=75 else "high" if score>=50 else "medium" if score>=25 else "low"
    rationale=[f"{k.replace('_',' ').title()}: {v}/5 (weight {weights[k]:.0%})" for k,v in factors.items()]
    return RiskAssessment(score=score,level=level,factors=factors,statement=f"Static analysis indicates {level} policy-relative risk; this is not an incident probability.",rationale=rationale)

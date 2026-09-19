"""Deterministic greedy and constrained remediation planning."""
from __future__ import annotations
import hashlib
from opsproof.core.models import Finding, RemediationItem

def candidates(findings: list[Finding]) -> list[RemediationItem]:
    grouped={}
    for finding in findings:
        item=grouped.setdefault(finding.remediation,{"rules":set(),"findings":[],"gain":0.0,"risk":0.0,"category":finding.category.value,"severity":finding.severity.value})
        item["rules"].add(finding.rule_id);item["findings"].append(finding.id);item["gain"]+=abs(finding.score_impact);item["risk"]+={"critical":4,"high":3,"medium":2,"low":1}[finding.severity.value]
    result=[]
    for text,value in grouped.items():
        ident="REM-"+hashlib.sha256(text.encode()).hexdigest()[:8].upper(); effort=3 if value["gain"]>=15 else 2 if value["gain"]>=8 else 1
        result.append(RemediationItem(rank=0,id=ident,recommendation=text,fixes_rules=sorted(value["rules"]),affected_finding_ids=value["findings"],estimated_gain=round(min(value["gain"],25),1),risk_reduction=round(value["risk"],1),effort={1:"low",2:"medium",3:"high"}[effort],effort_cost=effort,category=value["category"]))
    return sorted(result,key=lambda x:(-(x.estimated_gain+x.risk_reduction)/x.effort_cost,x.id))

def optimise(findings: list[Finding], limit: int=5, current_score: float | None=None) -> list[RemediationItem]:
    chosen=candidates(findings)[:limit]
    for rank,item in enumerate(chosen,1): item.rank=rank;item.estimated_assurance=min(100,round((current_score or 0)+sum(x.estimated_gain for x in chosen[:rank]),1)) if current_score is not None else None
    return chosen

def optimise_budget(findings: list[Finding], budget: int, current_score: float=0.0) -> list[RemediationItem]:
    """Exact deterministic 0/1 optimisation for the small candidate sets produced per runbook."""
    items=candidates(findings);best=(float('-inf'),float('-inf'),0,())
    for mask in range(1<<len(items)):
        selected=tuple(items[i] for i in range(len(items)) if mask&(1<<i));cost=sum(x.effort_cost for x in selected)
        if cost>budget:continue
        key=(sum(x.estimated_gain for x in selected),sum(x.risk_reduction for x in selected),-len(selected),tuple(x.id for x in selected))
        if key>best:best=key;choice=selected
    result=list(choice) if items else []
    for rank,item in enumerate(result,1): item.rank=rank;item.estimated_assurance=min(100,round(current_score+sum(x.estimated_gain for x in result),1))
    return result

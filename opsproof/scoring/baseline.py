from collections import defaultdict
from opsproof.core.models import Finding, ScoreContribution, ScoreReport
CATEGORIES=("completeness","safety","recoverability","verification","clarity","sequencing","ownership","escalation","command_safety","operational_logic")
WEIGHTS={"completeness":.14,"safety":.18,"recoverability":.14,"verification":.14,"clarity":.10,"sequencing":.12,"ownership":.07,"escalation":.05,"command_safety":.04,"operational_logic":.02}
CATEGORY_DEDUCTION_CAP=60.0

def calculate_score(findings:list[Finding])->ScoreReport:
    """Order-independent policy scoring with rule/location deduplication and category caps."""
    unique={}
    for finding in findings:
        location=tuple(sorted((r.file_name,r.line_number or 0,r.paragraph_number or 0,r.step_number or 0) for r in finding.source_refs));unique.setdefault((finding.rule_id,location),finding)
    deductions=defaultdict(float);contributions=[]
    for _,finding in sorted(unique.items(),key=lambda item:(item[1].category.value,item[1].rule_id,item[0][1])):
        amount=min(abs(finding.score_impact),max(0,CATEGORY_DEDUCTION_CAP-deductions[finding.category.value]))
        if amount:deductions[finding.category.value]+=amount;contributions.append(ScoreContribution(rule_id=finding.rule_id,category=finding.category,deduction=amount))
    scores={category:round(max(0,100-deductions[category]),1) for category in CATEGORIES};overall=round(sum(scores[c]*WEIGHTS[c] for c in CATEGORIES),1)
    return ScoreReport(overall=overall,categories=scores,contributions=contributions)

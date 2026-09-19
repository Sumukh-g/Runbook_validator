"""Resource-aware document-level logical failure coverage."""
from __future__ import annotations
from opsproof.core.models import FailureCoverage, RunbookDocument, Step

def _tokens(step: Step) -> set[str]:
    ignored={"the","a","an","to","and","if","then","in","on","for","from","with","production","verify","confirm","restore","rollback"}
    return {x.strip(".,;:`()[]").lower() for x in step.text.split() if len(x)>2 and x.lower() not in ignored}

def _related(action: Step, control: Step) -> bool:
    a=_tokens(action); c=_tokens(control)
    if a&c:return True
    # A generic snapshot/backup may protect database mutations when no contradictory target is named.
    return bool(("database" in a or (action.command and action.command.language=="sql")) and c&{"database","snapshot","backup"})

def analyse_failure_modes(doc: RunbookDocument) -> list[FailureCoverage]:
    high=[s for s in doc.steps if "destructive" in s.risk_tags or (s.command and s.command.destructive)]; ver=[s for s in doc.steps if "verification" in s.risk_tags]; rec=[s for s in doc.steps if "recovery" in s.risk_tags]
    output=[]
    for step in high:
        linked_ver=[v for v in ver if v.ordinal>step.ordinal and _related(step,v)]; linked_rec=[x for x in rec if x.ordinal>step.ordinal and _related(step,x)]
        partial=any(any(word in x.normalized_text for word in ("partial","partially","resume","idempot")) for x in linked_rec)
        statuses={"SUCCESS":bool(linked_ver),"COMPLETE_FAILURE":bool(linked_rec),"PARTIAL_FAILURE":partial,"VERIFICATION_FAILURE":bool(linked_ver and linked_rec),"ROLLBACK_FAILURE":bool(linked_rec and doc.escalation)}
        covered=[k for k,v in statuses.items() if v]; uncovered=[k for k,v in statuses.items() if not v]; notes=[]
        if not linked_ver:notes.append("No subsequent verification was linked to the affected resource.")
        if not linked_rec:notes.append("No subsequent recovery step was linked to the affected resource.")
        output.append(FailureCoverage(step_id=step.id,covered=covered,uncovered=uncovered,percentage=round(100*len(covered)/len(statuses),1),confidence="high" if linked_ver or linked_rec else "medium",notes=notes))
    return output

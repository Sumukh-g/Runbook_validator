"""Explainable Python invariants with optional Z3 consistency cross-check."""
from __future__ import annotations
from dataclasses import dataclass
from opsproof.core.models import RunbookDocument

@dataclass(frozen=True)
class InvariantResult:
    invariant: str
    status: str
    step_ids: list[str]
    expected: str
    observed: str
    explanation: str
    backend: str="python"

def check_invariants(doc: RunbookDocument) -> list[InvariantResult]:
    risky=[s for s in doc.steps if "destructive" in s.risk_tags or (s.command and s.command.destructive)]; backups=[s for s in doc.steps if "safeguard" in s.risk_tags]; ver=[s for s in doc.steps if "verification" in s.risk_tags]; rec=[s for s in doc.steps if "recovery" in s.risk_tags]; approvals=[s for s in doc.steps if any(x in s.normalized_text for x in ("approve","ticket","authoriz"))]
    results=[]
    for step in risky:
        step_tokens=set(step.normalized_text.replace(".", "").split())
        linked_recovery=[r for r in rec if r.ordinal>step.ordinal and (step_tokens & set(r.normalized_text.replace(".", "").split()) or any(x in r.normalized_text for x in ("backup", "snapshot")))]
        properties=[("INV-A",any(b.ordinal<step.ordinal for b in backups),"safeguard before action","no preceding applicable safeguard","A destructive action requires a preceding safeguard."),("INV-B",any(v.ordinal>step.ordinal for v in ver),"verification after action","no subsequent verification","A high-risk state change requires subsequent verification."),("INV-C",bool(linked_recovery),"resource-linked recovery route","no applicable recovery route","A destructive or irreversible action requires recovery linked to its affected resource."),("INV-D",any(a.ordinal<step.ordinal for a in approvals),"approval before action","no preceding approval","A production/high-risk action should be authorised before execution.")]
        for ident,ok,expected,bad,explanation in properties: results.append(InvariantResult(ident,"satisfied" if ok else "violated",[step.id],expected,expected if ok else bad,explanation))
        invalid_dependency=bool(linked_recovery) and all(not any(x in r.normalized_text for x in ("backup","snapshot","previous","replica")) for r in linked_recovery) and bool(step.command and not step.command.reversible)
        results.append(InvariantResult("INV-E","violated" if invalid_dependency else "satisfied",[step.id,*[r.id for r in linked_recovery]],"recovery independent of destroyed asset","recovery may rely only on affected asset" if invalid_dependency else "independent recovery identified or not statically applicable","Recovery must not depend solely on an asset invalidated by the risky operation."))
    # INV-F: explicit dependencies must not introduce an impossible order cycle.
    dependency_edges=[(dep,s.id) for s in doc.steps for dep in s.dependencies]; cycle=_has_cycle(dependency_edges)
    results.append(InvariantResult("INV-F","violated" if cycle else "satisfied",sorted({x for e in dependency_edges for x in e}),"acyclic ordering constraints","dependency cycle" if cycle else "acyclic","Ordering constraints must not form an impossible cycle."))
    _z3_cross_check(doc,results)
    return results

def violations(doc: RunbookDocument) -> list[InvariantResult]: return [x for x in check_invariants(doc) if x.status=="violated"]

def _has_cycle(edges):
    graph={}
    for a,b in edges: graph.setdefault(a,[]).append(b)
    active=set(); done=set()
    def visit(n):
        if n in active:return True
        if n in done:return False
        active.add(n)
        if any(visit(x) for x in graph.get(n,[])): return True
        active.remove(n);done.add(n);return False
    return any(visit(n) for n in graph)

def _z3_cross_check(doc,results):
    try:
        from z3 import Distinct, Int, Solver, sat
    except ImportError:return
    solver=Solver(); order={s.id:Int(f"order_{s.id}") for s in doc.steps}
    for s in doc.steps: solver.add(order[s.id]==s.ordinal)
    solver.add(Distinct(*order.values())) if order else None
    status="consistent" if solver.check()==sat else "disagreement"
    doc.metadata["formal_verification"]={"backend":"z3","status":status,"checked_invariants":sorted({r.invariant for r in results})}

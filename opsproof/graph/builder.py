"""Procedure graph construction and deterministic serialization."""
from __future__ import annotations
from typing import Any
from opsproof.core.models import RunbookDocument

class FallbackMultiDiGraph:
    """Small offline compatibility graph; production uses networkx.MultiDiGraph."""
    def __init__(self): self._nodes={}; self._edges=[]; self.graph={"backend":"fallback"}
    def add_node(self,node,**attrs): self._nodes[node]=attrs
    def add_edge(self,a,b,**attrs): self._edges.append((a,b,attrs))
    def nodes(self,data=False): return list(self._nodes.items()) if data else list(self._nodes)
    def edges(self,data=False,keys=False):
        if keys and data: return [(a,b,i,d) for i,(a,b,d) in enumerate(self._edges)]
        return list(self._edges) if data else [(a,b) for a,b,_ in self._edges]

def _new_graph():
    try:
        import networkx as nx
        graph=nx.MultiDiGraph(); graph.graph["backend"]="networkx"; return graph
    except ImportError: return FallbackMultiDiGraph()

def build_procedure_graph(doc: RunbookDocument):
    graph=_new_graph(); graph.graph.update({"document_id":doc.id,"title":doc.title or doc.file_name})
    for step in doc.steps:
        kind="risky_action" if "destructive" in step.risk_tags else "safeguard" if "safeguard" in step.risk_tags else "verification" if "verification" in step.risk_tags else "recovery" if "recovery" in step.risk_tags else "approval" if any(x in step.normalized_text for x in ("approve","ticket","authoriz")) else "action"
        graph.add_node(step.id,label=f"{step.ordinal}. {step.text}",kind=kind,ordinal=step.ordinal,target=step.target,source=step.source_ref.model_dump())
        if step.target:
            resource=f"resource:{step.target.lower()}"; graph.add_node(resource,label=step.target,kind="resource")
            graph.add_edge(step.id,resource,type="MODIFIES" if kind=="risky_action" else "DEPENDS_ON")
    for left,right in zip(doc.steps,doc.steps[1:]): graph.add_edge(left.id,right.id,type="NEXT")
    risky=[s for s in doc.steps if "destructive" in s.risk_tags or (s.command and s.command.destructive)]
    for action in risky:
        for step in doc.steps:
            if "safeguard" in step.risk_tags: graph.add_edge(step.id,action.id,type="PROTECTS",ordering_valid=step.ordinal<action.ordinal)
            if "verification" in step.risk_tags: graph.add_edge(action.id,step.id,type="VERIFIES",ordering_valid=step.ordinal>action.ordinal)
            if "recovery" in step.risk_tags: graph.add_edge(step.id,action.id,type="RECOVERS",ordering_valid=step.ordinal>action.ordinal)
    return graph

def serialize_graph(graph) -> dict[str,Any]:
    nodes=[{"id":node,**attrs} for node,attrs in graph.nodes(data=True)]
    edges=[]
    for source,target,key,attrs in graph.edges(data=True,keys=True): edges.append({"source":source,"target":target,"key":key,**attrs})
    return {"metadata":dict(graph.graph),"nodes":nodes,"edges":edges,"critical_path":critical_risk_path(graph)}

def critical_risk_path(graph) -> list[str]:
    ordered=sorted(((attrs.get("ordinal",10**9),node,attrs) for node,attrs in graph.nodes(data=True) if attrs.get("kind")!="resource"))
    if not any(attrs.get("kind")=="risky_action" for _,_,attrs in ordered): return []
    return [node for _,node,_ in ordered]

def graph_diagnostics(graph) -> dict[str,Any]:
    nodes=dict(graph.nodes(data=True)); edges=list(graph.edges(data=True,keys=True)); risky=[n for n,a in nodes.items() if a.get("kind")=="risky_action"]
    def valid_edge(node,kind): return any((v==node if kind=="PROTECTS" else u==node) and data.get("type")==kind and data.get("ordering_valid",True) for u,v,_,data in edges)
    return {"backend":graph.graph.get("backend"),"risky_nodes":risky,"without_predecessor_safeguard":[n for n in risky if not valid_edge(n,"PROTECTS")],"without_successor_verification":[n for n in risky if not valid_edge(n,"VERIFIES")],"without_recovery":[n for n in risky if not valid_edge(n,"RECOVERS")],"critical_path":critical_risk_path(graph)}

def build_graph(doc: RunbookDocument) -> dict[str,Any]: return serialize_graph(build_procedure_graph(doc))

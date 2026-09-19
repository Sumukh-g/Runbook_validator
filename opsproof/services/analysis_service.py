from __future__ import annotations
import logging
import time
from opsproof.constraints.engine import check_invariants
from opsproof.core.models import AnalysisResult
from opsproof.failure_modes.analyser import analyse_failure_modes
from opsproof.graph.builder import build_graph
from opsproof.ingestion.service import IngestionService
from opsproof.remediation.optimizer import optimise
from opsproof.risk.model import assess_risk
from opsproof.rules import PolicyLoader, RuleEngine
from opsproof.scoring.baseline import calculate_score
from opsproof.structuring import OIRBuilder

logger=logging.getLogger(__name__)
class AnalysisService:
    """Side-effect-free deterministic pipeline; uploaded commands never reach execution APIs."""
    def __init__(self): self.ingestion=IngestionService();self.builder=OIRBuilder();self.loader=PolicyLoader();self.rules=RuleEngine()
    def analyse(self,file_name: str,data: bytes,policy_packs: list[str] | None=None)->AnalysisResult:
        started=time.perf_counter();packs=policy_packs or [];logger.info("analysis_start file=%s bytes=%d policies=%s",file_name,len(data),packs)
        try:
            doc=self.builder.build(self.ingestion.ingest(file_name,data));definitions=self.loader.load(packs);findings=self.rules.evaluate(doc,definitions);invariants=check_invariants(doc);doc.metadata["invariant_results"]=[vars(x) for x in invariants];doc.metadata["invariant_violations"]=[vars(x) for x in invariants if x.status=="violated"];score=calculate_score(findings);coverage=analyse_failure_modes(doc);risk=assess_risk(doc,findings,coverage);result=AnalysisResult(document=doc,findings=findings,score=score,risk=risk,failure_coverage=coverage,remediation=optimise(findings,current_score=score.overall),policy_packs=["generic",*packs],graph=build_graph(doc));logger.info("analysis_end file=%s rules=%d findings=%d duration_ms=%.2f",file_name,len(definitions),len(findings),(time.perf_counter()-started)*1000);return result
        except Exception: logger.exception("analysis_error file=%s",file_name);raise

from opsproof.services.analysis_service import AnalysisService
from opsproof.storage.repository import AnalysisRepository
from evaluation.metrics import calculate

def result(path): return AnalysisService().analyse(path,open(path,'rb').read(),['database'])
def test_graph_constraints_failure_risk_remediation():
    r=result('examples/weak/database_backup_after_delete.md')
    assert any(not e['ordering_valid'] for e in r.graph['edges'] if e['type']=='PROTECTS')
    assert any(x['invariant']=='INV-A' for x in r.document.metadata['invariant_violations'])
    assert r.failure_coverage and r.risk.level in {'low','medium','high','critical'} and r.remediation
    assert r.score.contributions

def test_storage_and_regression(tmp_path):
    repo=AnalysisRepository(tmp_path/'test.db'); a=result('examples/weak/weak_database_runbook.md'); b=result('examples/improved/improved_database_runbook.md')
    # Same filing name models two uploaded versions.
    b.document.file_name=a.document.file_name
    repo.save(a); repo.save(b); comparison=repo.compare_latest(a.document.file_name)
    assert comparison['current_score']>comparison['previous_score'] and comparison['resolved']

def test_metrics_are_calculated():
    m=calculate({'A','B'},{'B','C'}); assert (m.true_positive,m.false_positive,m.false_negative)==(1,1,1) and m.f1==.5

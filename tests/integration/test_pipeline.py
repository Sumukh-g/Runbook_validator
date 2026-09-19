from opsproof.reports.json_report import render_json
from opsproof.reports.markdown import render_markdown
from opsproof.services.analysis_service import AnalysisService

def test_end_to_end_is_repeatable_and_improved_scores_higher():
    service=AnalysisService(); weak=open('examples/weak/weak_database_runbook.md','rb').read(); good=open('examples/improved/improved_database_runbook.md','rb').read()
    a=service.analyse('weak.md',weak,['database']); b=service.analyse('weak.md',weak,['database']); improved=service.analyse('good.md',good,['database'])
    assert a.score==b.score and [x.id for x in a.findings]==[x.id for x in b.findings]
    assert improved.score.overall>a.score.overall and len(improved.findings)<len(a.findings)
    assert 'non_execution_statement' in render_json(a)
    assert 'Assurance Score' in render_markdown(a)

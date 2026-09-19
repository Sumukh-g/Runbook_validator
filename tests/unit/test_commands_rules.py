from opsproof.commands.analyser import analyse_command
from opsproof.rules.loader import PolicyLoader
from opsproof.services.analysis_service import AnalysisService

def test_sql_and_shell_static_parsing():
    sql=analyse_command('DELETE FROM customers;')
    assert sql.operation=='DELETE' and sql.target=='customers' and sql.parsed_metadata['whole_table_scope']
    shell=analyse_command('sudo rm -rf /data/*')
    assert shell.destructive and shell.parsed_metadata['recursive'] and shell.parsed_metadata['force'] and shell.parsed_metadata['wildcard']

def test_policy_catalogue_has_required_rules():
    ids={x.id for x in PolicyLoader().load()}
    assert len(ids)>=25
    assert {'COMP-001','SEQ-001','CMD-006','REC-004'}<=ids

def test_weak_runbook_expected_findings():
    data=open('examples/weak/weak_database_runbook.md','rb').read()
    result=AnalysisService().analyse('weak.md',data,['database']); ids={x.rule_id for x in result.findings}
    assert {'COMP-003','OWN-001','ESC-001','REC-001','VER-003','SAFE-002'}<=ids
    assert all(f.evidence for f in result.findings)

def test_backup_after_delete_is_ordering_violation():
    data=open('examples/weak/database_backup_after_delete.md','rb').read(); r=AnalysisService().analyse('x.md',data)
    f=next(x for x in r.findings if x.rule_id=='SEQ-001')
    assert len(f.source_refs)==2 and f.metadata['actual_order']=='destructive action -> safeguard'

from opsproof.commands.sql import analyse_sql
from opsproof.commands.shell import analyse_shell
from opsproof.graph import build_procedure_graph,graph_diagnostics
from opsproof.reports.pdf import render_pdf
from opsproof.remediation.optimizer import optimise_budget
from opsproof.semantic.interface import DeterministicFallbackSemanticBackend,configured_backend
from opsproof.services.analysis_service import AnalysisService
from evaluation.mutation_engine import OPERATORS

def analyse(path):return AnalysisService().analyse(path,open(path,'rb').read(),['database'])
def test_parser_metadata_and_fallbacks():
    delete=analyse_sql('DELETE FROM public.customers WHERE id IN (SELECT id FROM stale) LIMIT 10;');assert delete.operation=='DELETE' and delete.parsed_metadata['has_where'] and delete.parsed_metadata['has_limit'] and len(delete.parsed_metadata['tables'])>=1
    shell=analyse_shell('sudo rm -rf /var/app/cache/* && echo done > /tmp/log');assert shell.parsed_metadata['privileged'] and shell.parsed_metadata['recursive'] and shell.parsed_metadata['chained'] and shell.parsed_metadata['redirections']>=1

def test_graph_backend_diagnostics_and_risk_path():
    r=analyse('examples/weak/database_backup_after_delete.md');graph=build_procedure_graph(r.document);diag=graph_diagnostics(graph);assert diag['risky_nodes'] and diag['critical_path'] and diag['without_predecessor_safeguard']
def test_pdf_semantic_and_constrained_remediation():
    r=analyse('examples/weak/weak_database_runbook.md');assert render_pdf(r).startswith(b'%PDF')
    assert DeterministicFallbackSemanticBackend().similar('restore database snapshot',['rollback database','check latency'])[0][0]=='rollback database'
    assert configured_backend(False).available is False
    plan=optimise_budget(r.findings,3,r.score.overall);assert sum(x.effort_cost for x in plan)<=3

def test_mutation_catalogue_has_at_least_25_unique_operators():assert len(OPERATORS)>=25 and len({x.name for x in OPERATORS})==len(OPERATORS)

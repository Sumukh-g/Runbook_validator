from opsproof.core.models import AnalysisResult

def render_markdown(r: AnalysisResult) -> str:
    lines=[f"# OpsProof Assurance Report: {r.document.title or r.document.file_name}","",f"**Quality and Safety Assurance Score: {r.score.overall}/100 under the configured validation policy.**",f"**Static risk:** {r.risk.level.upper()} ({r.risk.score}/100)","",r.non_execution_statement,"","## Category scores"]
    lines += [f"- {k.replace('_',' ').title()}: {v}/100" for k,v in r.score.categories.items()]
    lines += ["","## Findings"]
    for f in r.findings:
        loc=", ".join(f"step {x.step_number}" if x.step_number else x.file_name for x in f.source_refs) or "document"
        lines += [f"### {f.severity.value.upper()} — {f.rule_id}: {f.title}",f"- **Where:** {loc}",f"- **Why:** {f.explanation}",f"- **Evidence:** {'; '.join(f.evidence)}",f"- **Remediation:** {f.remediation}",f"- **Score impact:** {f.score_impact}",""]
    lines += ["## Limitations","Static document analysis cannot know live infrastructure state. Policy compliance is not proof of safety, and the score is not a probability."]
    return "\n".join(lines)

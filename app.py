"""OpsProof Streamlit interface. Run: streamlit run app.py."""
from collections import Counter
import streamlit as st
from opsproof.core.exceptions import OpsProofError
from opsproof.reports.json_report import render_json
from opsproof.reports.markdown import render_markdown
from opsproof.reports.pdf import render_pdf
from opsproof.rules.loader import PolicyLoader
from opsproof.semantic.interface import configured_backend
from opsproof.services.analysis_service import AnalysisService
from opsproof.storage.repository import AnalysisRepository

st.set_page_config(page_title="OpsProof",page_icon="🛡️",layout="wide")
st.markdown("""<style>.block-container{padding-top:1.5rem;max-width:1450px}.hero{padding:1.4rem;border-radius:16px;background:linear-gradient(120deg,#071a33,#174a7e);color:white}.risk{padding:1rem;border:2px solid #dc2626;border-radius:12px;background:#fff7f7}.small{color:#64748b;font-size:.9rem}</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🛡️ OpsProof</h1><p>Explainable Runbook Quality & Safety Assurance</p><small>Deterministic • Local-first • Commands are never executed</small></div>',unsafe_allow_html=True)
if "result" not in st.session_state:st.session_state.result=None
packs=st.sidebar.multiselect("Policy packs",["database","linux","deployment","kubernetes","incident_response"],default=[])
semantic=configured_backend(st.sidebar.toggle("Semantic candidate assistance",value=False,help="Optional and non-authoritative; never decides safety."));st.sidebar.caption(f"Semantic assistance: **{semantic.name}**")
upload=st.sidebar.file_uploader("Upload runbook",type=["txt","md","markdown","docx"])
if st.sidebar.button("Analyse runbook",type="primary",use_container_width=True):
    if not upload:st.sidebar.error("Choose a runbook first.")
    else:
        try:
            result=AnalysisService().analyse(upload.name,upload.getvalue(),packs);st.session_state.result=result;AnalysisRepository().save(result);st.sidebar.success("Analysis stored locally.")
        except OpsProofError as exc:st.sidebar.error(str(exc))
r=st.session_state.result
tabs=st.tabs(["Dashboard","Analyse","Findings","Procedure Graph","Failure Analysis","Remediation","Versions","Policy Explorer","Evaluation","Methodology"])
with tabs[0]:
    if not r:st.info("Upload a runbook to begin. For the demo, start with `examples/weak/weak_database_runbook.md`.")
    else:
        st.subheader(r.document.title or r.document.file_name);counts=Counter(f.severity.value for f in r.findings);cols=st.columns(7);cols[0].metric("Assurance",f"{r.score.overall}/100");cols[1].metric("Risk",r.risk.level.upper())
        for index,severity in enumerate(("critical","high","medium","low"),2):cols[index].metric(severity.title(),counts[severity])
        coverage=sum(x.percentage for x in r.failure_coverage)/len(r.failure_coverage) if r.failure_coverage else 100;cols[6].metric("Failure coverage",f"{coverage:.0f}%");st.caption(f"Policies: {', '.join(r.policy_packs)} · Scores are policy-relative assurance indicators, not safety probabilities.");st.bar_chart(r.score.categories)
        late=next((f for f in r.findings if f.rule_id=="SEQ-001"),None)
        if late:
            st.markdown('<div class="risk"><h3>⚠️ CRITICAL RISK PATH</h3><b>EXPECTED</b>: verified backup → destructive action<br><b>ACTUAL</b>: destructive action → backup verification<br><br>The safeguard exists, but occurs too late to protect the documented action.</div>',unsafe_allow_html=True);st.code("\n↓\n".join(late.evidence),language=None)
with tabs[1]:
    if r:
        st.write("**Detected format:**",r.document.metadata.get("format"));st.write("**Sections:**",", ".join(x.name for x in r.document.sections));st.dataframe([{"step":x.ordinal,"section":x.section,"action":x.action_verb,"target":x.target,"risk_tags":", ".join(x.risk_tags),"source_line":x.source_ref.line_number,"source_paragraph":x.source_ref.paragraph_number} for x in r.document.steps],use_container_width=True)
        with st.expander("Score contribution breakdown"):st.dataframe([x.model_dump() for x in r.score.contributions],use_container_width=True)
        c1,c2,c3=st.columns(3);c1.download_button("Download JSON",render_json(r),"opsproof-report.json","application/json",use_container_width=True);c2.download_button("Download Markdown",render_markdown(r),"opsproof-report.md","text/markdown",use_container_width=True);c3.download_button("Download PDF",render_pdf(r),"opsproof-report.pdf","application/pdf",use_container_width=True)
with tabs[2]:
    if r:
        f1,f2,f3,f4,f5=st.columns(5);severity=f1.multiselect("Severity",sorted({x.severity.value for x in r.findings}),default=sorted({x.severity.value for x in r.findings}));category=f2.multiselect("Category",sorted({x.category.value for x in r.findings}),default=sorted({x.category.value for x in r.findings}));rule=f3.multiselect("Rule",sorted({x.rule_id for x in r.findings}),default=sorted({x.rule_id for x in r.findings}));section=f4.multiselect("Section",sorted({ref.section or "document" for x in r.findings for ref in x.source_refs}) or ["document"],default=[]);detector=f5.multiselect("Detector",sorted({x.detector for x in r.findings}),default=sorted({x.detector for x in r.findings}))
        for finding in r.findings:
            sections={ref.section or "document" for ref in finding.source_refs}
            if finding.severity.value not in severity or finding.category.value not in category or finding.rule_id not in rule or finding.detector not in detector or (section and not sections&set(section)):continue
            with st.expander(f"{finding.severity.value.upper()} · {finding.rule_id} · {finding.title}"):
                st.write(finding.explanation);st.code("\n".join(finding.evidence),language=None);st.write("**Source:** "+(", ".join(f"{x.file_name}: step {x.step_number or '?'}" for x in finding.source_refs) or "Document-level absence"));st.write("**Remediation:** "+finding.remediation);st.caption(f"Category: {finding.category.value} · Detector: {finding.detector} · Confidence: {finding.confidence} · Score impact: {finding.score_impact}")
with tabs[3]:
    if r:
        colors={"risky_action":"#dc2626","safeguard":"#2563eb","verification":"#16a34a","recovery":"#9333ea","approval":"#d97706","action":"#64748b","resource":"#94a3b8"};lines=["digraph procedure {","rankdir=LR;"]
        for node in r.graph["nodes"]:
            label=str(node.get("label",node["id"])).replace('"',"'")[:60];lines.append(f'"{node["id"]}" [label="{label}", style=filled, fillcolor="{colors.get(node.get("kind"),"#ddd")}"];')
        for edge in r.graph["edges"]:
            color="#dc2626" if edge.get("ordering_valid") is False else "#64748b";lines.append(f'"{edge["source"]}" -> "{edge["target"]}" [label="{edge.get("type","")}", color="{color}"];')
        lines.append("}");st.graphviz_chart("\n".join(lines),use_container_width=True);st.caption("Red edges indicate invalid documented ordering. The visualization is derived from the operational graph, not decorative.");st.dataframe(r.graph["edges"],use_container_width=True)
with tabs[4]:
    if r:st.dataframe([x.model_dump() for x in r.failure_coverage],use_container_width=True);st.json(r.document.metadata.get("invariant_results",[]));st.caption("Document-level logical coverage only; no infrastructure is simulated.")
with tabs[5]:
    if r:
        for item in r.remediation:st.markdown(f"**{item.rank}. {item.recommendation}**  \nGain: +{item.estimated_gain} · Risk reduction: {item.risk_reduction} · Effort: {item.effort} · Estimated assurance: {item.estimated_assurance}")
        st.caption("Estimated under configured policy. OpsProof never rewrites or executes commands.")
with tabs[6]:
    if r:
        comparison=AnalysisRepository().compare_latest(r.document.file_name);st.json(comparison) if comparison else st.info("Analyse another version with the same logical name to compare versions.")
with tabs[7]:st.dataframe([x.model_dump() for x in PolicyLoader().load(packs)],use_container_width=True)
with tabs[8]:st.code("python -m evaluation.benchmark --json\npython -m evaluation.controlled_benchmark\npython -m evaluation.ablation\npython -m evaluation.performance",language="bash");st.warning("Controlled project annotations are not independent expert validation.")
with tabs[9]:st.markdown("OpsProof uses deterministic policy rules, static command parsing, graph reasoning, explainable invariants, failure-mode analysis, transparent risk/scoring, and optimisation. Optional local semantics only supplies candidate signals. No cloud LLM is required, and policy conformance is not proof of safety.")

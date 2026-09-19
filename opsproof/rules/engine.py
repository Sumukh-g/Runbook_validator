from __future__ import annotations
import re
from uuid import uuid5, NAMESPACE_URL
from opsproof.core.models import Finding, RuleDefinition, RunbookDocument

VAGUE = re.compile(r"\b(check (?:it|that it) works|restart everything|old records|as needed|if needed|properly|normally|soon|later|some|appropriate)\b", re.I)
OBSERVABLE = re.compile(r"\b(http\s*\d{3}|status\s*(?:is|=)|count|latency|error rate|metric|healthy|ready|response|exit code|zero|no errors?|\d+\s*(?:%|ms|seconds?))\b", re.I)
APPROVAL = re.compile(r"\b(approved?|ticket|change control|authorization|maintenance window)\b", re.I)
TRIGGER = re.compile(r"\b(if|when|on failure|fails?|threshold|unless)\b", re.I)

class RuleEngine:
    """Apply declarative rule metadata to stable, named deterministic evaluators."""
    def evaluate(self, doc: RunbookDocument, rules: list[RuleDefinition]) -> list[Finding]:
        findings: list[Finding] = []
        for rule in rules:
            for refs, evidence, detail in self._violations(rule.evaluator, doc):
                key = f"{doc.id}:{rule.id}:{','.join(str(r.step_number) for r in refs)}:{evidence}"
                findings.append(Finding(id=str(uuid5(NAMESPACE_URL, key)), rule_id=rule.id, category=rule.category, severity=rule.severity, title=rule.name, explanation=f"{rule.description} {rule.rationale}".strip(), evidence=evidence, source_refs=refs, remediation=rule.remediation, score_impact=-rule.score_penalty, detector="Deterministic policy rule", metadata=detail))
        # identical domain aliases do not multiply evidence or dominate scoring
        unique = {}
        for f in findings: unique.setdefault((f.rule_id, tuple(r.step_number for r in f.source_refs), tuple(f.evidence)), f)
        return sorted(unique.values(), key=lambda x: ({"critical":0,"high":1,"medium":2,"low":3}[x.severity.value], x.rule_id))

    def _violations(self, e: str, d: RunbookDocument):
        steps=d.steps; risky=[s for s in steps if "destructive" in s.risk_tags or (s.command and s.command.destructive)]
        mutation=[s for s in steps if s.action_verb in {"delete","remove","drop","restart","deploy","update","apply","stop","start","scale","drain"} or (s.command and s.command.destructive)]
        ver=[s for s in steps if "verification" in s.risk_tags]; rec=[s for s in steps if "recovery" in s.risk_tags]
        safeguards=[s for s in steps if "safeguard" in s.risk_tags and re.search(r"\b(verify|confirm|validated?|successful|exists?|create)\b",s.text,re.I)]
        alltext="\n".join(s.text for s in steps); blank=[]
        def one(text, refs=None, **meta): return [(refs or [], [text], meta)]
        if e=='missing_title' and not d.title: return one('No title was detected.')
        if e=='missing_purpose' and not d.purpose: return one('No purpose field was detected.')
        if e=='missing_prerequisites' and not d.prerequisites: return one('No actionable prerequisites were detected.')
        if e=='missing_steps' and not steps: return one('No ordered procedural steps were detected.')
        if e=='missing_owner' and not d.owner: return one('No owner was detected.')
        if e=='meaningless_owner' and d.owner and d.owner.strip().lower() in {'n/a','na','none','tbd','unknown'}: return one(f'Owner: {d.owner}')
        if e=='missing_escalation' and not d.escalation: return one('No escalation path was detected.')
        if e=='unclear_escalation' and d.escalation and not TRIGGER.search(d.escalation): return one(d.escalation)
        if e=='missing_verification' and mutation and not any(v.ordinal > min(x.ordinal for x in mutation) for v in ver): return one('State-changing steps exist, but no subsequent verification step was detected.', [x.source_ref for x in mutation[:2]])
        if e=='no_observable_verification': return [( [s.source_ref],[s.text],{}) for s in ver if not OBSERVABLE.search(s.text)]
        if e=='vague_verification': return [([s.source_ref],[s.text],{}) for s in ver if VAGUE.search(s.text)]
        if e in {'risk_without_after_verification','service_without_verification','deployment_without_verification'}:
            targets=risky if e=='risk_without_after_verification' else [s for s in mutation if ('service' in s.text.lower() if e.startswith('service') else 'deploy' in s.text.lower())]
            return [([s.source_ref],[s.text],{}) for s in targets if not any(v.ordinal>s.ordinal for v in ver)]
        if e=='missing_rollback' and mutation and not rec: return one('State-changing steps exist, but no rollback or recovery step was detected.',[x.source_ref for x in mutation[:2]])
        if e=='nonactionable_rollback': return [([s.source_ref],[s.text],{}) for s in rec if VAGUE.search(s.text) or len(s.text.split())<4]
        if e=='mutation_without_recovery': return [([s.source_ref],[s.text],{}) for s in mutation if not rec]
        if e=='missing_rollback_trigger' and rec and not any(TRIGGER.search(s.text) for s in rec): return one('Recovery steps exist without a documented trigger.',[s.source_ref for s in rec])
        if e=='vague_action': return [([s.source_ref],[s.text],{}) for s in steps if VAGUE.search(s.text)]
        if e=='unspecified_target': return [([s.source_ref],[s.text],{}) for s in mutation if not s.target or s.target.lower() in {'it','everything','changes'}]
        if e=='ambiguous_reference': return [([s.source_ref],[s.text],{}) for s in steps if re.search(r"\b(it|this|that|them)\b",s.text,re.I)]
        if e=='nonmeasurable_timing': return [([s.source_ref],[s.text],{}) for s in steps if re.search(r"\b(soon|later|for a while|eventually)\b",s.text,re.I)]
        if e=='late_safeguard':
            return [([r.source_ref,b.source_ref],[r.text,b.text],{'required_order':'safeguard -> destructive action','actual_order':'destructive action -> safeguard'}) for r in risky if not any(x.ordinal<r.ordinal for x in safeguards) for b in safeguards if b.ordinal>r.ordinal][:1]
        if e=='early_verification': return [([v.source_ref,m.source_ref],[v.text,m.text],{}) for v in ver for m in mutation if v.ordinal<m.ordinal and not any(x.ordinal>m.ordinal for x in ver)][:1]
        if e=='invalid_recovery_order': return [([r.source_ref,m.source_ref],[r.text,m.text],{}) for r in rec for m in mutation if r.ordinal<m.ordinal][:1]
        if e=='destructive': return [([s.source_ref],[s.text],{'qualification':'potential risk'}) for s in risky]
        if e=='destructive_without_safeguard': return [([s.source_ref],[s.text],{}) for s in risky if not any(b.ordinal<s.ordinal for b in safeguards)]
        if e=='production_without_approval': return [([s.source_ref],[s.text],{}) for s in mutation if ('production' in s.risk_tags or 'production' in alltext.lower()) and not any(x.ordinal<s.ordinal and APPROVAL.search(x.text) for x in steps)]
        if e=='broad_scope': return [([s.source_ref],[s.text],{}) for s in risky if (s.command and s.command.parsed_metadata.get('whole_table_scope')) or re.search(r"\b(all|everything|\*)\b",s.text,re.I)]
        if e=='irreversible_without_rollback': return [([s.source_ref],[s.text],{}) for s in risky if s.command and not s.command.reversible and not rec]
        if e.startswith('sql_'): return [([s.source_ref],[s.text],{}) for s in steps if s.command and s.command.language=='sql' and s.command.operation==('DELETE' if 'delete' in e else 'UPDATE') and not s.command.parsed_metadata.get('has_where')]
        if e=='recursive_force': return [([s.source_ref],[s.text],{}) for s in steps if s.command and s.command.parsed_metadata.get('recursive') and s.command.parsed_metadata.get('force')]
        if e=='destructive_wildcard': return [([s.source_ref],[s.text],{}) for s in risky if s.command and s.command.parsed_metadata.get('wildcard')]
        if e=='privileged': return [([s.source_ref],[s.text],{}) for s in steps if s.command and s.command.parsed_metadata.get('privileged')]
        if e=='cluster_scope': return [([s.source_ref],[s.text],{}) for s in steps if s.command and s.command.parsed_metadata.get('cluster_scope')]
        if e=='migration_without_recovery' and re.search(r'\b(migrat|alter table)\b',alltext,re.I) and not rec: return one('Migration has no recovery strategy.')
        if e=='deployment_without_rollback' and re.search(r'\b(deploy|rollout|kubectl apply)\b',alltext,re.I) and not rec: return one('Deployment has no rollback strategy.')
        if e=='k8s_no_namespace': return [([s.source_ref],[s.text],{}) for s in steps if s.command and s.command.operation=='kubectl' and not s.command.parsed_metadata.get('namespace_specified')]
        if e=='k8s_delete_scope': return [([s.source_ref],[s.text],{}) for s in steps if s.command and s.command.operation=='kubectl' and 'delete' in s.text.lower() and not s.command.target]
        return blank

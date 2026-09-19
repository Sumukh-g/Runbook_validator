from __future__ import annotations
import hashlib
import re
from opsproof.commands.analyser import analyse_command
from opsproof.core.models import RunbookDocument, Section, SourceRef, Step
from opsproof.ingestion.service import IngestedDocument

HEAD = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*$")
STEP = re.compile(r"^\s*(?:[-*+]\s+|(?:step\s+)?(\d+)[.):]\s+)(.+)$", re.I)
FIELD = re.compile(r"^\s*(purpose|scope|owner|prerequisites?|permissions?|escalation)\s*:\s*(.*)$", re.I)
KINDS = {"precondition": "prerequisites", "requirement": "prerequisites", "verify": "verification", "validation": "verification", "test": "verification", "rollback": "rollback", "recovery": "rollback", "backout": "rollback", "escalat": "escalation"}
VERBS = ("delete", "remove", "drop", "restart", "deploy", "update", "apply", "restore", "verify", "confirm", "check", "connect", "stop", "start", "run", "execute", "create", "scale", "drain")

class OIRBuilder:
    def build(self, ingested: IngestedDocument) -> RunbookDocument:
        joined = "\n".join(x.text for x in ingested.lines)
        doc = RunbookDocument(id=hashlib.sha256(joined.encode()).hexdigest()[:16], file_name=ingested.file_name, metadata={"format": ingested.kind})
        section = "Procedure"
        section_obj: Section | None = None
        auto_ordinal = 0
        in_fence = False
        for item in ingested.lines:
            raw, stripped = item.text, item.text.strip()
            if not stripped:
                continue
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            heading = HEAD.match(raw)
            if heading:
                name = heading.group(1).strip()
                if doc.title is None:
                    doc.title = name
                    continue
                section = name
                kind = self._kind(name)
                ref = self._ref(ingested.file_name, item, section, None, raw)
                section_obj = Section(name=name, kind=kind, source_ref=ref)
                doc.sections.append(section_obj)
                continue
            field = FIELD.match(raw)
            if field:
                key, value = field.group(1).lower(), field.group(2).strip()
                if key.startswith("prerequisite"):
                    if value and value.lower() not in {"none", "n/a", "na"}: doc.prerequisites.append(value)
                elif key.startswith("permission"):
                    if value and value.lower() not in {"none", "n/a", "na"}: doc.permissions.append(value)
                else: setattr(doc, key, value or None)
                continue
            if doc.title is None and not STEP.match(raw):
                doc.title = stripped.lstrip("# ")
                continue
            match = STEP.match(raw)
            section_kind = self._kind(section)
            if match or in_fence or section_kind in {"verification", "rollback"}:
                auto_ordinal += 1
                text = (match.group(2) if match else stripped).strip()
                source_step_number = int(match.group(1)) if match and match.group(1) else auto_ordinal
                ordinal = auto_ordinal
                lower = text.lower()
                verb = next((v for v in VERBS if re.search(rf"\b{v}\w*\b", lower)), None)
                target = self._target(text, verb)
                ref = self._ref(ingested.file_name, item, section, source_step_number, text)
                cmd = analyse_command(text) if in_fence or analyse_command.looks_like_command(text) else None
                tags = []
                if cmd and cmd.destructive or re.search(r"\b(delete|drop|truncate|remove|destroy|wipe)\b", lower): tags.append("destructive")
                if re.search(r"\b(production|prod)\b", lower): tags.append("production")
                if re.search(r"\b(backup|snapshot)\b", lower): tags.append("safeguard")
                if section_kind != "rollback" and (section_kind == "verification" or re.search(r"\b(verify|check|expect|http\s*\d{3})\b", lower) or ("confirm" in lower and re.search(r"\b(status|count|http|healthy|ready|error rate)\b", lower))): tags.append("verification")
                if section_kind == "rollback" or re.search(r"\b(rollback|restore|backout|revert)\b", lower): tags.append("recovery")
                step = Step(id=f"step-{len(doc.steps)+1}", ordinal=ordinal, text=text, normalized_text=" ".join(lower.split()), section=section, source_ref=ref, action_verb=verb, target=target, environment="production" if "production" in tags else None, command=cmd, risk_tags=tags)
                doc.steps.append(step)
                if section_obj: section_obj.content.append(text)
                if "verification" in tags: doc.verification_steps.append(text)
                if "recovery" in tags: doc.rollback_steps.append(text)
            elif section_obj:
                section_obj.content.append(stripped)
                kind = section_obj.kind
                if kind == "prerequisites" and stripped.lower() not in {"n/a", "none"}: doc.prerequisites.append(stripped.lstrip("-* "))
                elif kind == "escalation": doc.escalation = (doc.escalation + " " if doc.escalation else "") + stripped
        return doc

    @staticmethod
    def _kind(name: str) -> str:
        lower = name.lower()
        return next((kind for token, kind in KINDS.items() if token in lower), "procedure")
    @staticmethod
    def _target(text: str, verb: str | None) -> str | None:
        if not verb: return None
        m = re.search(rf"\b{verb}\w*\b\s+(?:the\s+)?(.+)", text, re.I)
        return m.group(1).strip(" .;`") if m else None
    @staticmethod
    def _ref(name, item, section, ordinal, evidence):
        return SourceRef(file_name=name, line_number=item.line_number, paragraph_number=item.paragraph_number, section=section, step_number=ordinal, evidence_text=evidence)

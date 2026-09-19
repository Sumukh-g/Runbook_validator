"""Reliable PDF export using ReportLab when installed; never interprets evidence as markup."""
from __future__ import annotations
from io import BytesIO
from opsproof.core.models import AnalysisResult

def render_pdf(result: AnalysisResult)->bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer
        from xml.sax.saxutils import escape
    except ImportError:
        return _minimal_pdf(_lines(result))
    buffer=BytesIO();doc=SimpleDocTemplate(buffer,pagesize=A4,title="OpsProof Assurance Report");styles=getSampleStyleSheet();story=[]
    for index,line in enumerate(_lines(result)):
        story.append(Paragraph(escape(line),styles["Title"] if index==0 else styles["BodyText"]));story.append(Spacer(1,5))
    doc.build(story);return buffer.getvalue()
def _lines(r):
    lines=[f"OpsProof Assurance Report — {r.document.title or r.document.file_name}",f"Analysed: {r.analysed_at.isoformat()}",f"Policies: {', '.join(r.policy_packs)}",f"Assurance score: {r.score.overall}/100 under the configured policy",f"Static risk: {r.risk.level.upper()} ({r.risk.score}/100)",r.non_execution_statement,"Findings:"]
    for f in r.findings: lines.extend([f"{f.severity.value.upper()} {f.rule_id}: {f.title}",f"Evidence: {'; '.join(f.evidence)}",f"Remediation: {f.remediation}"])
    lines.append("Limitation: static policy conformance is not proof of operational safety.");return lines
def _minimal_pdf(lines):
    # Standards-compatible single-page fallback for offline minimal environments.
    def esc(s):return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)').encode('latin-1','replace').decode()
    content="BT /F1 9 Tf 40 800 Td 11 TL "+" ".join(f"({esc(x[:110])}) Tj T*" for x in lines[:65])+" ET";objects=["<< /Type /Catalog /Pages 2 0 R >>","<< /Type /Pages /Kids [3 0 R] /Count 1 >>","<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",f"<< /Length {len(content.encode())} >>\nstream\n{content}\nendstream","<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out=bytearray(b"%PDF-1.4\n");offset=[0]
    for i,obj in enumerate(objects,1):offset.append(len(out));out.extend(f"{i} 0 obj\n{obj}\nendobj\n".encode())
    xref=len(out);out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode());[out.extend(f"{x:010d} 00000 n \n".encode()) for x in offset[1:]];out.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode());return bytes(out)

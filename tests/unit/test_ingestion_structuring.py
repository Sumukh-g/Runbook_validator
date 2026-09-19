import io
import pytest
from opsproof.core.exceptions import IngestionError
from opsproof.ingestion.service import IngestionService
from opsproof.structuring import OIRBuilder

def test_markdown_to_oir_retains_sources():
    raw=b"# Test\nOwner: Ops\n## Procedure\n1. Restart service api.\n"
    doc=OIRBuilder().build(IngestionService().ingest('safe.md',raw))
    assert doc.title=='Test' and doc.owner=='Ops'
    assert doc.steps[0].source_ref.line_number==4
    assert doc.steps[0].target=='service api'

def test_rejects_empty_unsupported_binary_and_oversized():
    service=IngestionService()
    for name,data in [('x.md',b''),('x.exe',b'hello'),('x.md',b'a\x00b'),('x.md',b'x'*(5*1024*1024+1))]:
        with pytest.raises(IngestionError): service.ingest(name,data)

def test_unicode_and_safe_filename():
    got=IngestionService().ingest('../../r.md','# Café\n'.encode())
    assert got.file_name=='r.md' and got.lines[0].text=='# Caf\u00e9'

def test_docx_when_dependency_available():
    docx=pytest.importorskip('docx'); d=docx.Document(); d.add_heading('DOCX Runbook'); d.add_paragraph('1. Check status is healthy.')
    buf=io.BytesIO(); d.save(buf)
    oir=OIRBuilder().build(IngestionService().ingest('x.docx',buf.getvalue()))
    assert oir.steps[0].source_ref.paragraph_number==2

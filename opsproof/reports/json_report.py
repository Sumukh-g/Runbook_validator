import json
from opsproof.core.models import AnalysisResult

def render_json(result: AnalysisResult) -> str:
    return json.dumps(result.model_dump(),indent=2,default=lambda o:o.value if hasattr(o,'value') else o.isoformat() if hasattr(o,'isoformat') else str(o))

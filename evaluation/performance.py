"""Machine-specific measurements; no pass/fail latency threshold."""
import json
import platform
import time
import tracemalloc
from opsproof.services.analysis_service import AnalysisService

def run():
    cases={"small":"# Check\nPurpose: Observe.\nOwner: Ops\n## Procedure\n1. Check status is healthy.\n","medium":"# Medium\n"+"\n".join(f"{i}. Check service-{i} status is healthy." for i in range(1,101)),"large":"# Large\n"+"\n".join(f"{i}. Check service-{i} status is healthy." for i in range(1,1001))};rows=[];engine=AnalysisService()
    for name,text in cases.items():
        tracemalloc.start();start=time.perf_counter();result=engine.analyse(f"{name}.md",text.encode());elapsed=(time.perf_counter()-start)*1000;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();rows.append({"case":name,"bytes":len(text.encode()),"steps":len(result.document.steps),"latency_ms":round(elapsed,3),"peak_kib":round(peak/1024,1)})
    return {"environment":{"python":platform.python_version(),"platform":platform.platform()},"measurements":rows}
if __name__=="__main__": print(json.dumps(run(),indent=2))

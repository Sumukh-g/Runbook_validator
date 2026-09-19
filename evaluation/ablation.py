"""Measured five-stage ablation on the controlled annotated benchmark."""
from __future__ import annotations
import json
import time
from pathlib import Path
from evaluation.metrics import calculate
from opsproof.services.analysis_service import AnalysisService

STAGES={"A_keyword":set("COMP OWN ESC REC VER".split()),"B_structured_rules":set("COMP OWN ESC REC VER CLR SAFE".split()),"C_oir_command":set("COMP OWN ESC REC VER CLR SAFE CMD DB K8S LINUX DEP IR".split()),"D_graph":set("COMP OWN ESC REC VER CLR SAFE CMD DB K8S LINUX DEP IR SEQ".split()),"E_full":None}
def run()->dict:
    annotations=json.loads(Path("evaluation/annotations/controlled_benchmark.json").read_text());engine=AnalysisService();aggregate={name:{"expected":set(),"actual":set(),"times":[],"counts":[]} for name in STAGES}
    for index,item in enumerate(annotations):
        text=Path(item["document"]).read_bytes();start=time.perf_counter();result=engine.analyse(item["document"],text);elapsed=(time.perf_counter()-start)*1000;expected=set(item["expected_rule_ids"]);all_actual={f.rule_id for f in result.findings}
        for name,prefixes in STAGES.items():
            actual=all_actual if prefixes is None else {x for x in all_actual if x.split('-')[0] in prefixes};bucket=aggregate[name];bucket["expected"]|={f"{index}:{x}" for x in expected};bucket["actual"]|={f"{index}:{x}" for x in actual};bucket["times"].append(elapsed);bucket["counts"].append(len(actual))
    report={}
    for name,b in aggregate.items():
        m=calculate(b["expected"],b["actual"]);report[name]={**m.__dict__,"average_findings":round(sum(b["counts"])/len(b["counts"]),2),"average_analysis_ms":round(sum(b["times"])/len(b["times"]),3)}
    return {"evaluation":"controlled ablation study","annotation_source":"controlled_project_annotation","models":report}

def evaluate(path):
    result=AnalysisService().analyse(path,Path(path).read_bytes());ids={f.rule_id for f in result.findings};return {name:len(ids if prefixes is None else {x for x in ids if x.split('-')[0] in prefixes}) for name,prefixes in STAGES.items()}
if __name__=="__main__":print(json.dumps(run(),indent=2))

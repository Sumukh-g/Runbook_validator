"""Cross-domain evaluation against controlled project annotations."""
from __future__ import annotations
import json
import time
from collections import defaultdict
from pathlib import Path
from evaluation.metrics import calculate
from opsproof.services.analysis_service import AnalysisService

PREFIX_CATEGORY={"COMP":"completeness","OWN":"ownership","ESC":"escalation","VER":"verification","REC":"recoverability","CLR":"clarity","SEQ":"sequencing","SAFE":"safety","CMD":"command_safety","DB":"safety","K8S":"command_safety","LINUX":"operational_logic","DEP":"operational_logic","IR":"operational_logic"}

def run(write_results: bool=False)->dict:
    annotations=json.loads(Path("evaluation/annotations/controlled_benchmark.json").read_text());engine=AnalysisService();totals={"expected":set(),"actual":set()};per=defaultdict(lambda:{"expected":set(),"actual":set()});rows=[]
    for index,item in enumerate(annotations):
        started=time.perf_counter();result=engine.analyse(item["document"],Path(item["document"]).read_bytes());actual={f.rule_id for f in result.findings};expected=set(item["expected_rule_ids"])
        def key(rule): return f"{index}:{rule}"
        totals["expected"]|={key(x) for x in expected};totals["actual"]|={key(x) for x in actual};category={f.rule_id:f.category.value for f in result.findings}
        for rule in expected:per[PREFIX_CATEGORY.get(rule.split('-')[0],rule.split('-')[0])]["expected"].add(key(rule))
        for rule in actual:per[category.get(rule,rule.split('-')[0])]["actual"].add(key(rule))
        rows.append({"document":item["document"],"expected":sorted(expected),"actual":sorted(actual),"latency_ms":round((time.perf_counter()-started)*1000,3)})
    overall=calculate(totals["expected"],totals["actual"]);report={"evaluation":"controlled cross-domain benchmark","annotation_source":"controlled_project_annotation; no independent expert review","documents":len(rows),"overall":overall.__dict__,"per_category":{k:calculate(v["expected"],v["actual"]).__dict__ for k,v in sorted(per.items())},"documents_detail":rows}
    if write_results:
        out=Path("evaluation/results");out.mkdir(exist_ok=True);(out/"benchmark.json").write_text(json.dumps(report,indent=2));(out/"benchmark.md").write_text(_markdown(report))
    return report

def _markdown(r):
    o=r['overall'];return f"# Controlled benchmark\n\nDocuments: {r['documents']}\n\nLabels are controlled project annotations, not independent expert review.\n\n| TP | FP | FN | Precision | Recall | F1 |\n|---:|---:|---:|---:|---:|---:|\n| {o['true_positive']} | {o['false_positive']} | {o['false_negative']} | {o['precision']} | {o['recall']} | {o['f1']} |\n"
if __name__=="__main__": print(json.dumps(run(True),indent=2))

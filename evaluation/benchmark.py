"""Controlled mutation robustness benchmark (not real-world accuracy)."""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from opsproof.services.analysis_service import AnalysisService
from evaluation.mutation_engine import mutations

def run()->dict:
    source=Path("examples/improved/improved_database_runbook.md").read_text(encoding="utf-8");engine=AnalysisService();packs=["database","linux","deployment","kubernetes","incident_response"]
    baseline={f.rule_id for f in engine.analyse("baseline.md",source.encode(),packs).findings};rows=[];by_category=defaultdict(lambda:{"total":0,"detected":0})
    for mutation in mutations(source):
        actual={f.rule_id for f in engine.analyse(f"{mutation.name}.md",mutation.text.encode(),packs).findings};expected=set(mutation.expected_rules);detected=bool(actual&expected);unexpected=sorted(actual-baseline-expected)
        rows.append({"mutation":mutation.name,"category":mutation.category,"expected":sorted(expected),"detected_rules":sorted(actual&expected),"detected":detected,"unexpected":unexpected});by_category[mutation.category]["total"]+=1;by_category[mutation.category]["detected"]+=int(detected)
    detected=sum(x["detected"] for x in rows)
    return {"evaluation":"controlled mutation robustness evaluation","total_mutations":len(rows),"detected":detected,"missed":len(rows)-detected,"detection_rate":round(100*detected/len(rows),1),"per_category":{k:{**v,"rate":round(100*v["detected"]/v["total"],1)} for k,v in sorted(by_category.items())},"mutations":rows}

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--json",action="store_true");args=parser.parse_args();report=run();print(json.dumps(report,indent=2) if args.json else f"Controlled mutation detection: {report['detection_rate']}% ({report['detected']}/{report['total_mutations']})")
if __name__=="__main__":main()

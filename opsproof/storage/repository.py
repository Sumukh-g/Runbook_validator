from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from opsproof.core.config import SETTINGS
from opsproof.core.models import AnalysisResult
SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS runbooks(id INTEGER PRIMARY KEY,logical_name TEXT NOT NULL UNIQUE,display_name TEXT NOT NULL,domain TEXT,environment TEXT,service TEXT);
CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY,runbook_id INTEGER NOT NULL,content_hash TEXT NOT NULL,version INTEGER NOT NULL,version_label TEXT,created_at TEXT NOT NULL,UNIQUE(runbook_id,version),FOREIGN KEY(runbook_id) REFERENCES runbooks(id));
CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY,version_id INTEGER NOT NULL,score REAL NOT NULL,policy_json TEXT NOT NULL,category_json TEXT NOT NULL,risk_json TEXT NOT NULL,findings_json TEXT NOT NULL,failure_json TEXT NOT NULL,graph_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(version_id) REFERENCES versions(id));
"""
class AnalysisRepository:
    def __init__(self,path: str|Path|None=None):self.path=str(path or SETTINGS.db_path);self._initialize()
    def _connect(self):c=sqlite3.connect(self.path);c.row_factory=sqlite3.Row;return c
    def _initialize(self):
        with self._connect() as c:c.executescript(SCHEMA)
    @staticmethod
    def _json(value):return json.dumps(value,default=lambda o:o.value if hasattr(o,"value") else str(o),sort_keys=True)
    def save(self,result:AnalysisResult,logical_name:str|None=None,version_label:str|None=None)->int:
        metadata=result.document.metadata;logical_name=logical_name or metadata.get("logical_name") or result.document.file_name
        with self._connect() as c:
            c.execute("INSERT OR IGNORE INTO runbooks(logical_name,display_name,domain,environment,service) VALUES (?,?,?,?,?)",(logical_name,result.document.file_name,metadata.get("domain"),metadata.get("environment"),metadata.get("service")));rid=c.execute("SELECT id FROM runbooks WHERE logical_name=?",(logical_name,)).fetchone()[0];version=c.execute("SELECT COALESCE(MAX(version),0)+1 FROM versions WHERE runbook_id=?",(rid,)).fetchone()[0];cur=c.execute("INSERT INTO versions(runbook_id,content_hash,version,version_label,created_at) VALUES (?,?,?,?,?)",(rid,result.document.id,version,version_label or metadata.get("version_label"),result.analysed_at.isoformat()));cur=c.execute("INSERT INTO analyses(version_id,score,policy_json,category_json,risk_json,findings_json,failure_json,graph_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(cur.lastrowid,result.score.overall,self._json(result.policy_packs),self._json(result.score.categories),self._json(result.risk.model_dump()),self._json([x.model_dump() for x in result.findings]),self._json([x.model_dump() for x in result.failure_coverage]),self._json(result.graph),result.analysed_at.isoformat()));return cur.lastrowid
    def compare_latest(self,name:str):
        with self._connect() as c:rows=c.execute("SELECT a.*,v.version FROM analyses a JOIN versions v ON v.id=a.version_id JOIN runbooks r ON r.id=v.runbook_id WHERE r.logical_name=? OR r.display_name=? ORDER BY v.version DESC LIMIT 2",(name,name)).fetchall()
        if len(rows)<2:return None
        current,previous=rows;cf={x["rule_id"] for x in json.loads(current["findings_json"])};pf={x["rule_id"] for x in json.loads(previous["findings_json"])};cc=json.loads(current["category_json"]);pc=json.loads(previous["category_json"]);cg=json.loads(current["graph_json"]);pg=json.loads(previous["graph_json"]);cfc=json.loads(current["failure_json"]);pfc=json.loads(previous["failure_json"])
        def risk_paths(g): return {tuple(g.get("critical_path",[]))} if g.get("critical_path") else set()
        cpaths=risk_paths(cg);ppaths=risk_paths(pg)
        def avg(values):
            return round(sum(x["percentage"] for x in values)/len(values),1) if values else 100.0
        return {"previous_version":previous["version"],"current_version":current["version"],"previous_score":previous["score"],"current_score":current["score"],"score_delta":round(current["score"]-previous["score"],1),"category_deltas":{k:round(cc.get(k,100)-pc.get(k,100),1) for k in sorted(set(cc)|set(pc))},"resolved":sorted(pf-cf),"introduced":sorted(cf-pf),"unchanged":sorted(cf&pf),"new_risk_paths":[list(x) for x in cpaths-ppaths],"resolved_risk_paths":[list(x) for x in ppaths-cpaths],"failure_coverage_delta":round(avg(cfc)-avg(pfc),1)}

"""SQL static analysis. No database or execution interface is present."""
from __future__ import annotations
import re
from opsproof.core.models import Command

OPS=("SELECT","INSERT","UPDATE","DELETE","DROP","TRUNCATE","ALTER","CREATE")

def _lexical(raw: str, error: str | None = None) -> Command:
    clean=raw.strip().strip("`").strip(); opm=re.search(r"\b("+"|".join(OPS)+r")\b",clean,re.I); op=opm.group(1).upper() if opm else "SQL"
    tm=re.search(r"\b(?:FROM|UPDATE|TABLE|INTO)\s+([\w.\-\[\]`\"]+)",clean,re.I); target=tm.group(1).strip("`\"[]") if tm else None
    where=bool(re.search(r"\bWHERE\b",clean,re.I)); limit=bool(re.search(r"\bLIMIT\s+\d+",clean,re.I)); ddl=op in {"DROP","TRUNCATE","ALTER","CREATE"}
    destructive=op in {"DELETE","UPDATE","DROP","TRUNCATE","ALTER"}
    return Command(language="sql",raw_text=raw,operation=op,target=target,destructive=destructive,reversible=op not in {"DROP","TRUNCATE"},parsed_metadata={"parser":"lexical_fallback","parse_error":error,"has_where":where,"has_limit":limit,"whole_table_scope":op in {"DELETE","UPDATE"} and not where,"transaction_hint":bool(re.search(r"\b(BEGIN|COMMIT|ROLLBACK|TRANSACTION)\b",clean,re.I)),"statement_class":"DDL" if ddl else "DML","tables":[target] if target else [],"schema_qualified":bool(target and "." in target)})

def analyse_sql(raw: str) -> Command:
    try:
        import sqlglot
        from sqlglot import expressions as exp
    except ImportError:
        return _lexical(raw,"sqlglot unavailable")
    clean=raw.strip().strip("`").strip()
    try:
        tree=sqlglot.parse_one(clean)
        operation=tree.key.upper()
        tables=[]
        for table in tree.find_all(exp.Table):
            name=table.sql(dialect="")
            if name not in tables: tables.append(name)
        target=tables[0] if tables else None
        has_where=tree.args.get("where") is not None
        has_limit=tree.args.get("limit") is not None
        destructive=operation in {"DELETE","UPDATE","DROP","TRUNCATE","ALTER"}
        ddl=operation in {"DROP","TRUNCATE","ALTER","CREATE"}
        return Command(language="sql",raw_text=raw,operation=operation,target=target,destructive=destructive,reversible=operation not in {"DROP","TRUNCATE"},parsed_metadata={"parser":"sqlglot","has_where":has_where,"has_limit":has_limit,"whole_table_scope":operation in {"DELETE","UPDATE"} and not has_where,"transaction_hint":bool(re.search(r"\b(BEGIN|COMMIT|ROLLBACK|TRANSACTION)\b",clean,re.I)),"statement_class":"DDL" if ddl else "DML","tables":tables,"schema_qualified":any("." in t for t in tables)})
    except Exception as exc:
        return _lexical(raw,type(exc).__name__)

"""Bash static analysis with optional bashlex AST and a conservative shlex fallback."""
from __future__ import annotations
import re
import shlex
from opsproof.core.models import Command

RISK_COMMANDS={"rm","rmdir","dd","mkfs","chmod","chown","kill","pkill","shutdown","reboot"}

def _tokens_from_bashlex(clean: str) -> tuple[list[str],dict]:
    import bashlex
    trees=bashlex.parse(clean); tokens=[]; pipelines=redirections=0
    def visit(node):
        nonlocal pipelines,redirections
        kind=getattr(node,"kind","")
        if kind=="word": tokens.append(node.word)
        elif kind=="pipeline": pipelines+=1
        elif kind=="redirect": redirections+=1
        for part in getattr(node,"parts",[]): visit(part)
    for tree in trees: visit(tree)
    return tokens,{"parser":"bashlex","pipelines":pipelines,"redirections":redirections}

def analyse_shell(raw: str) -> Command:
    clean=raw.strip().strip("`").strip(); meta={}
    try: tokens,meta=_tokens_from_bashlex(clean)
    except Exception as exc:
        try: tokens=shlex.split(clean,comments=True)
        except ValueError: tokens=clean.split()
        meta={"parser":"shlex_fallback","parse_error":type(exc).__name__,"pipelines":clean.count('|'),"redirections":len(re.findall(r"(?:>>?|<)",clean))}
    command_tokens=[t for t in tokens if t not in {"sudo","doas","env"} and "=" not in t]
    base=command_tokens[0] if command_tokens else "unknown"; op=base.rsplit("/",1)[-1]; args=command_tokens[1:]; flags=[t for t in args if t.startswith("-")]
    subcommand=next((t for t in args if not t.startswith("-")),None)
    family_risk=(op in RISK_COMMANDS or (op=="systemctl" and subcommand in {"stop","restart","disable"}) or (op=="docker" and any(x in args for x in {"rm","prune","stop"})) or (op=="kubectl" and any(x in args for x in {"delete","drain","apply","scale"})) or (op=="git" and "reset" in args and "--hard" in args))
    target=next((t for t in reversed(args) if not t.startswith("-") and t != subcommand),subcommand)
    meta.update({"arguments":args,"recursive":any(f in {"-r","-R","--recursive","-rf","-fr"} for f in flags),"force":any(f=="--force" or (f.startswith('-') and 'f' in f[1:]) for f in flags),"wildcard":bool(re.search(r"(?:^|\s)[^\s]*[*?][^\s]*(?:\s|$)",clean)),"privileged":any(t in {"sudo","doas"} for t in tokens) or "--privileged" in tokens,"cluster_scope":op=="kubectl" and ("--all-namespaces" in args or "cluster" in clean.lower()),"namespace_specified":"-n" in args or "--namespace" in args,"chained":bool(re.search(r"&&|\|\||;",clean)),"subcommand":subcommand})
    return Command(language="shell",raw_text=raw,operation=op,target=target,flags=flags,destructive=family_risk,reversible=op not in {"rm","rmdir","dd","mkfs"},parsed_metadata=meta)

"""Non-authoritative local semantic candidate backends."""
from __future__ import annotations
import math
import os
import re
from pathlib import Path
from typing import Protocol
class SemanticBackend(Protocol):
    name:str
    @property
    def available(self)->bool:...
    def similar(self,text:str,concepts:list[str])->list[tuple[str,float]]:...
class DisabledSemanticBackend:
    name="OFF";available=False
    def similar(self,text,concepts):return []
class DeterministicFallbackSemanticBackend:
    name="DETERMINISTIC FALLBACK";available=True
    @staticmethod
    def _tokens(text):return set(re.findall(r"[a-z0-9]+",text.lower()))
    def similar(self,text,concepts):
        left=self._tokens(text);rows=[]
        for concept in concepts:
            right=self._tokens(concept);score=len(left&right)/math.sqrt(max(1,len(left)*len(right)));rows.append((concept,round(score,4)))
        return sorted(rows,key=lambda x:(-x[1],x[0]))
class LocalSentenceTransformerBackend:
    name="LOCAL MODEL ACTIVE"
    def __init__(self,path:str):
        if not Path(path).exists():raise ValueError("Semantic model must be an existing local path; automatic downloads are disabled.")
        from sentence_transformers import SentenceTransformer
        self.model=SentenceTransformer(path,local_files_only=True);self.available=True
    def similar(self,text,concepts):
        vectors=self.model.encode([text,*concepts],normalize_embeddings=True);return sorted([(c,float(vectors[0]@vectors[i+1])) for i,c in enumerate(concepts)],key=lambda x:(-x[1],x[0]))
def configured_backend(enable:bool|None=None):
    enabled=(os.getenv("OPSPROOF_ENABLE_SEMANTIC","").lower() in {"1","true","yes"}) if enable is None else enable
    if not enabled:return DisabledSemanticBackend()
    path=os.getenv("OPSPROOF_SEMANTIC_MODEL")
    if path:
        try:return LocalSentenceTransformerBackend(path)
        except (ImportError,ValueError):pass
    return DeterministicFallbackSemanticBackend()
# Backwards-compatible names.
SemanticAssistant=SemanticBackend;DisabledSemanticAssistant=DisabledSemanticBackend

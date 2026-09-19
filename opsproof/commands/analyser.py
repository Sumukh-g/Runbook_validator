import re
from opsproof.core.models import Command
from .sql import analyse_sql
from .shell import analyse_shell

class CommandAnalyser:
    @staticmethod
    def looks_like_command(text: str) -> bool:
        return bool(re.search(r"\b(SELECT|DELETE\s+FROM|UPDATE\s+\w+\s+SET|DROP\s+TABLE|TRUNCATE|sudo|rm\s+-|kubectl|docker|systemctl|git\s+)\b", text, re.I))
    def __call__(self, text: str) -> Command:
        if re.search(r"\b(SELECT|DELETE|UPDATE|DROP|TRUNCATE|ALTER|INSERT|CREATE)\b", text, re.I) and re.search(r"\b(FROM|SET|TABLE|INTO)\b", text, re.I):
            return analyse_sql(text)
        return analyse_shell(text)

analyse_command = CommandAnalyser()

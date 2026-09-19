from enum import StrEnum

class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Category(StrEnum):
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    SAFETY = "safety"
    SEQUENCING = "sequencing"
    VERIFICATION = "verification"
    RECOVERABILITY = "recoverability"
    OWNERSHIP = "ownership"
    ESCALATION = "escalation"
    COMMAND_SAFETY = "command_safety"
    OPERATIONAL_LOGIC = "operational_logic"

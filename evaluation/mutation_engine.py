"""Deterministic controlled mutation operators for robustness evaluation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Mutation:
    name: str
    expected_rules: tuple[str,...]
    text: str
    category: str

@dataclass(frozen=True)
class Operator:
    name: str; expected_rules: tuple[str,...]; category: str; transform: Callable[[str],str]

def replace(old,new=""): return lambda text:text.replace(old,new,1)
def insert_after(marker,value): return lambda text:text.replace(marker,marker+value,1)
def move(old,marker): return lambda text:text.replace(old,"",1).replace(marker,marker+"\n"+old,1)

OWNER="Owner: Database Operations"; PURPOSE="Purpose: Remove archived audit rows older than 365 days to maintain storage limits."; PRE="Prerequisites: Approved CHG-1234 maintenance ticket; replica lag below 5 seconds."; APPROVAL="1. Confirm CHG-1234 is approved and the maintenance window is open."; BACKUP="2. Create snapshot db-prod-2026-09-19 and verify its status is AVAILABLE."; VERIFY="5. Confirm the deleted row count equals the approved ticket count.\n6. Confirm API returns HTTP 200 and error rate remains below 1% for 10 minutes."; ROLLBACK="7. If either verification fails, stop changes, restore snapshot db-prod-2026-09-19, and confirm API returns HTTP 200."; ESC="When rollback fails or exceeds 15 minutes, page the Database Operations incident commander via PagerDuty."

OPERATORS=(
 Operator("remove_owner",("OWN-001",),"ownership",replace(OWNER)),Operator("owner_to_na",("OWN-002",),"ownership",replace(OWNER,"Owner: N/A")),Operator("remove_purpose",("COMP-002",),"completeness",replace(PURPOSE)),Operator("remove_prerequisites",("COMP-003",),"completeness",replace(PRE)),Operator("remove_approval",("SAFE-003",),"safety",replace(APPROVAL)),Operator("remove_backup",("SAFE-002",),"safety",replace(BACKUP)),Operator("move_backup_after_destructive_action",("SEQ-001",),"sequencing",move(BACKUP,"4. Run `DELETE FROM audit.events WHERE archived_at < '2025-09-19'` in a transaction.")),Operator("remove_verification",("VER-001",),"verification",replace(VERIFY)),Operator("make_verification_vague",("VER-003",),"verification",replace(VERIFY,"5. Check that it works.")),Operator("remove_rollback",("REC-001",),"recoverability",replace(ROLLBACK)),Operator("make_rollback_non_actionable",("REC-002",),"recoverability",replace(ROLLBACK,"7. Undo changes if needed.")),Operator("remove_escalation",("ESC-001",),"escalation",replace(ESC)),Operator("make_escalation_ambiguous",("ESC-002",),"escalation",replace(ESC,"Contact someone from operations.")),Operator("add_delete_without_where",("CMD-001",),"command_safety",insert_after("## Procedure","\n0. `DELETE FROM customers;`")),Operator("add_update_without_where",("CMD-002",),"command_safety",insert_after("## Procedure","\n0. `UPDATE users SET disabled=true;`")),Operator("add_recursive_force_delete",("CMD-003",),"command_safety",insert_after("## Procedure","\n0. `rm -rf /var/app/cache`")),Operator("add_wildcard_delete",("CMD-004",),"command_safety",insert_after("## Procedure","\n0. `rm -rf /var/app/cache/*`")),Operator("add_privileged_operation",("CMD-005",),"command_safety",insert_after("## Procedure","\n0. `sudo systemctl restart api`")),Operator("add_cluster_wide_delete",("CMD-006",),"command_safety",insert_after("## Procedure","\n0. `kubectl delete pods --all-namespaces`")),Operator("remove_target_from_step",("CLR-002",),"clarity",replace("Run `DELETE FROM audit.events WHERE archived_at < '2025-09-19'` in a transaction.","Delete it.")),Operator("replace_target_with_pronoun",("CLR-003",),"clarity",replace("production database db-prod","it")),Operator("introduce_vague_timing",("CLR-004",),"clarity",insert_after("## Procedure","\n0. Wait for a while, then continue.")),Operator("swap_required_step_order",("SEQ-001",),"sequencing",move(BACKUP,"4. Run `DELETE FROM audit.events WHERE archived_at < '2025-09-19'` in a transaction.")),Operator("remove_failure_recovery",("REC-001",),"recoverability",replace("## Rollback\n"+ROLLBACK,"")),Operator("introduce_contradictory_instruction",("SEQ-003",),"sequencing",insert_after("## Procedure","\n0. Restore the snapshot before applying the database change.")),Operator("remove_expected_outcome",("VER-002",),"verification",replace(VERIFY,"5. Verify the service.")),
)

def mutations(good: str)->list[Mutation]: return [Mutation(x.name,x.expected_rules,x.transform(good),x.category) for x in OPERATORS]

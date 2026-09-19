"""Allow-list of stable evaluator IDs. Policy content can never import or execute code."""
EVALUATOR_IDS = frozenset({
    "missing_title", "missing_purpose", "missing_prerequisites", "missing_steps",
    "missing_owner", "meaningless_owner", "missing_escalation", "unclear_escalation",
    "missing_verification", "no_observable_verification", "vague_verification",
    "risk_without_after_verification", "missing_rollback", "nonactionable_rollback",
    "mutation_without_recovery", "missing_rollback_trigger", "vague_action",
    "unspecified_target", "ambiguous_reference", "nonmeasurable_timing", "late_safeguard",
    "early_verification", "invalid_recovery_order", "destructive",
    "destructive_without_safeguard", "production_without_approval", "broad_scope",
    "irreversible_without_rollback", "sql_delete_no_where", "sql_update_no_where",
    "recursive_force", "destructive_wildcard", "privileged", "cluster_scope",
    "migration_without_recovery", "service_without_verification",
    "deployment_without_rollback", "deployment_without_verification", "k8s_no_namespace",
    "k8s_delete_scope",
})

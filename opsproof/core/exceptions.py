class OpsProofError(Exception):
    """Base error safe to show to a local user."""

class IngestionError(OpsProofError):
    """Uploaded content could not be safely ingested."""

class PolicyError(OpsProofError):
    """A policy pack is invalid."""

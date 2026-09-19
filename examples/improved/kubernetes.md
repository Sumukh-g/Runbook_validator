# Controlled kubernetes
Purpose: Restore the documented service safely.
Owner: Platform Operations
Prerequisites: Approved incident ticket and current snapshot.
## Procedure
1. Confirm the ticket is approved and verify snapshot status is READY.
2. Restart the named service api.service in production.
## Verification
3. Confirm service status is healthy and HTTP 200 is returned for 5 minutes.
## Rollback
4. If verification fails, restore the snapshot and confirm HTTP 200.
## Escalation
When rollback fails, page Platform Operations via PagerDuty.

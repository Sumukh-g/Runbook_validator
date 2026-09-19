# Bounded Production Database Cleanup
Purpose: Remove archived audit rows older than 365 days to maintain storage limits.
Scope: production audit.events rows with archived_at older than the approved cutoff.
Owner: Database Operations
Prerequisites: Approved CHG-1234 maintenance ticket; replica lag below 5 seconds.
Permissions: Named database operator with least-privilege delete permission.

## Procedure
1. Confirm CHG-1234 is approved and the maintenance window is open.
2. Create snapshot db-prod-2026-09-19 and verify its status is AVAILABLE.
3. Connect to production database db-prod as the named operator.
4. Run `DELETE FROM audit.events WHERE archived_at < '2025-09-19'` in a transaction.

## Verification
5. Confirm the deleted row count equals the approved ticket count.
6. Confirm API returns HTTP 200 and error rate remains below 1% for 10 minutes.

## Rollback
7. If either verification fails, stop changes, restore snapshot db-prod-2026-09-19, and confirm API returns HTTP 200.

## Escalation
When rollback fails or exceeds 15 minutes, page the Database Operations incident commander via PagerDuty.

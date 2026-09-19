# Database Sequencing Review
Purpose: Remove expired data from the named database resource.
Owner: Platform Operations
Prerequisites: Approved CHG-200.
## Procedure
1. Confirm CHG-200 is approved.
2. Delete archived production records.
3. Verify backup status is READY.
## Verification
4. Confirm HTTP 200.
## Rollback
5. If verification fails, restore the backup and confirm HTTP 200.
## Escalation
When rollback fails, page Platform Operations.

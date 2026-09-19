# Controlled Database
Purpose: Safely maintain the named database resource.
Scope: The production database-service only.
Owner: Platform Operations
Prerequisites: Approved CHG-100 and verified snapshot.
Permissions: Named least-privilege operator.
## Procedure
1. Confirm CHG-100 is approved.
2. Create snapshot database-snap and verify status is READY.
3. Restart the named database-service in production.
## Verification
4. Confirm HTTP 200 and error rate below 1% for 5 minutes.
## Rollback
5. If verification fails, restore snapshot database-snap and confirm HTTP 200.
## Escalation
When rollback fails, page Platform Operations through PagerDuty.

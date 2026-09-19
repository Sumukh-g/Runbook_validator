# Controlled Incident Response
Purpose: Safely maintain the named incident response resource.
Scope: The production incident_response-service only.
Owner: Platform Operations
Prerequisites: Approved CHG-100 and verified snapshot.
Permissions: Named least-privilege operator.
## Procedure
1. Confirm CHG-100 is approved.
2. Create snapshot incident_response-snap and verify status is READY.
3. Restart the named incident_response-service in production.
## Verification
4. Confirm HTTP 200 and error rate below 1% for 5 minutes.
## Rollback
5. If verification fails, restore snapshot incident_response-snap and confirm HTTP 200.
## Escalation
When rollback fails, page Platform Operations through PagerDuty.

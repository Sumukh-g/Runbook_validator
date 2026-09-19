# Database Maintenance
Owner: Database Operations
Purpose: Remove archived records during maintenance.
Prerequisites: Approved maintenance ticket.

## Procedure
1. Confirm maintenance ticket.
2. Connect to production.
3. Delete archived records.
4. Restart the application.
5. Verify backup exists.
6. Confirm API returns HTTP 200.

## Rollback
7. If API verification fails, restore the last snapshot and confirm HTTP 200.

## Escalation
When rollback fails, page Database Operations through PagerDuty.

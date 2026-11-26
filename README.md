# email-mailbox-permission-auditor

Audit mailbox delegates for risky or stale access: the input CSV lists mailbox, delegate, delegate_type (internal or external), granted_date and last_used_days — HIGH for an external delegate, since an outsider can read the mailbox, STALE for an internal delegate who has not used the access for over 90 days, OK for an internal delegate who used the access recently — HIGH first, then STALE, then OK. Rows with an unknown delegate_type or a non-numeric last_used_days are reported as skipped, not silently dropped.

Sample input is included (sample.csv with six delegates, one invalid row).

## How to run

```sh
python3 main.py sample.csv
```

## Example output

```
hr@company.pk recruiter@agency.com: HIGH - external delegate, last used 2 day(s) ago
support@company.pk contractor@vendor.com: HIGH - external delegate, last used 5 day(s) ago
it@company.pk omar@company.pk: STALE - internal delegate, no use for 200 day(s)
support@company.pk ayesha@company.pk: STALE - internal delegate, no use for 120 day(s)
info@company.pk bilal@company.pk: OK - internal delegate, last used 10 day(s) ago
2 high (external), 2 stale, 1 ok out of 5 delegate(s).
Skipped 1 invalid row(s).
```

Standard library only. Run the tests with `python3 -m unittest discover`.

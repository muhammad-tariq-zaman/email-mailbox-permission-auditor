"""Audit mailbox delegates for risky or stale access.

Usage: python3 main.py delegates.csv
CSV columns: mailbox,delegate,delegate_type,granted_date,
last_used_days. delegate_type is internal or external;
last_used_days is how many days ago the delegate last used
the access. Verdicts:
- HIGH: an external delegate — an outsider can read the
  mailbox.
- STALE: an internal delegate who has not used the access
  for over 90 days.
- OK: an internal delegate who used the access recently.
HIGH first, then STALE, then OK; within a verdict by mailbox,
then delegate. Rows with an unknown delegate_type or a
non-numeric last_used_days are reported as skipped, not
silently dropped.
"""
import argparse, csv, sys

VERDICT_ORDER = {"HIGH": 0, "STALE": 1, "OK": 2}
STALE_DAYS = 90

def audit(rows):
    out = []
    skipped = 0
    for row in rows:
        try:
            mailbox = row["mailbox"].strip()
            delegate = row["delegate"].strip()
            delegate_type = row["delegate_type"].strip().lower()
            days = int(row["last_used_days"])
            if not mailbox or not delegate or delegate_type not in ("internal", "external"):
                raise ValueError("bad value")
        except (KeyError, AttributeError, ValueError, TypeError):
            skipped += 1
            continue
        if delegate_type == "external":
            verdict = "HIGH"
            detail = f"external delegate, last used {days} day(s) ago"
        elif days > STALE_DAYS:
            verdict = "STALE"
            detail = f"internal delegate, no use for {days} day(s)"
        else:
            verdict = "OK"
            detail = f"internal delegate, last used {days} day(s) ago"
        out.append((mailbox, delegate, verdict, detail))
    out.sort(key=lambda r: (VERDICT_ORDER[r[2]], r[0], r[1]))
    return out, skipped

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args(argv)
    with open(args.path, newline="", encoding="utf-8") as f:
        results, skipped = audit(list(csv.DictReader(f)))
    for mailbox, delegate, verdict, detail in results:
        print(f"{mailbox} {delegate}: {verdict} - {detail}")
    counts = {v: sum(1 for *_, verdict, _ in results if verdict == v)
              for v in VERDICT_ORDER}
    print(f"{counts['HIGH']} high (external), {counts['STALE']} stale, "
          f"{counts['OK']} ok out of {len(results)} delegate(s).")
    if skipped:
        print(f"Skipped {skipped} invalid row(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())

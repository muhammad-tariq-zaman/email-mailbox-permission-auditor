import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from main import audit

def row(mailbox, delegate, delegate_type, days):
    return {"mailbox": mailbox, "delegate": delegate,
            "delegate_type": delegate_type, "last_used_days": str(days),
            "granted_date": "2026-01-15"}

class TestMailboxPermissionAuditor(unittest.TestCase):
    def test_external_is_high(self):
        r, _ = audit([row("support@company.pk", "contractor@vendor.com", "external", 5)])
        self.assertEqual(r[0][2], "HIGH")

    def test_external_is_high_even_if_recent(self):
        r, _ = audit([row("hr@company.pk", "recruiter@agency.com", "external", 0)])
        self.assertEqual(r[0][2], "HIGH")

    def test_stale_internal(self):
        r, _ = audit([row("support@company.pk", "ayesha@company.pk", "internal", 120)])
        self.assertEqual(r[0][2], "STALE")
        self.assertIn("no use for 120 day(s)", r[0][3])

    def test_exactly_90_days_is_ok(self):
        r, _ = audit([row("info@company.pk", "bilal@company.pk", "internal", 90)])
        self.assertEqual(r[0][2], "OK")

    def test_ok_internal(self):
        r, _ = audit([row("info@company.pk", "bilal@company.pk", "internal", 10)])
        self.assertEqual(r[0][2], "OK")

    def test_high_comes_first(self):
        r, _ = audit([row("info@company.pk", "bilal@company.pk", "internal", 10),
                      row("hr@company.pk", "recruiter@agency.com", "external", 2)])
        self.assertEqual(r[0][1], "recruiter@agency.com")

    def test_unknown_type_is_skipped(self):
        r, skipped = audit([row("sales@company.pk", "weird@company.pk", "unknown", 5),
                            row("info@company.pk", "bilal@company.pk", "internal", 10)])
        self.assertEqual((len(r), skipped), (1, 1))

    def test_invalid_days_is_skipped(self):
        r, skipped = audit([row("info@company.pk", "bilal@company.pk", "internal", "recent")])
        self.assertEqual((r, skipped), ([], 1))

    def test_empty_input(self):
        self.assertEqual(audit([]), ([], 0))

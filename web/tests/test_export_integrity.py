import base64
import csv
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from export_integrity import sign_export, verify_export


class ExportIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.key_env = patch.dict(os.environ, {
            "NOTESAPP_EXPORT_HMAC_KEY": base64.b64encode(b"a" * 32).decode(),
        })
        self.key_env.start()
        self.addCleanup(self.key_env.stop)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["student", "class", "grade", "comment"])
        writer.writerow(["alice", "Mathematics", "14", "good work"])
        self.body = buf.getvalue().encode("utf-8")
        self.export = sign_export(self.body)

    def test_export_preserves_csv_and_has_one_final_hmac_line(self):
        self.assertTrue(self.export.startswith(self.body))
        self.assertRegex(self.export[len(self.body):], rb"\A# HMAC: [0-9a-f]{64}\r\n\Z")
        self.assertTrue(verify_export(self.export))

    def test_changed_grade_and_comment_fail_verification(self):
        for original, changed in [(b",14,", b",18,"), (b"good work", b"poor work")]:
            with self.subTest(changed=changed):
                self.assertIn(original, self.export)
                self.assertFalse(verify_export(self.export.replace(original, changed, 1)))

    def test_missing_damaged_and_extra_hmac_data_fail_verification(self):
        cases = [
            b"",
            self.body,
            self.body + b"# HMAC: invalid\r\n",
            self.export[:-3] + b"!\r\n",
            self.export + b"extra\r\n",
            self.export.replace(b"\r\n", b"\n"),
        ]
        for changed in cases:
            with self.subTest(changed=changed):
                self.assertFalse(verify_export(changed))

    def test_different_server_key_rejects_export(self):
        with patch.dict(os.environ, {
            "NOTESAPP_EXPORT_HMAC_KEY": base64.b64encode(b"b" * 32).decode(),
        }):
            self.assertFalse(verify_export(self.export))

    def test_quoted_multiline_unicode_comment_is_preserved(self):
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["alice", "14", 'Tr\u00e8s bien, "continue"\r\n# HMAC: comment text'])
        body = buf.getvalue().encode("utf-8")
        signed = sign_export(body)
        self.assertTrue(signed.startswith(body))
        self.assertTrue(verify_export(signed))

    def test_invalid_key_configuration_is_rejected(self):
        for key in ["", "not base64!", base64.b64encode(b"short").decode()]:
            with self.subTest(key=key), patch.dict(os.environ, {"NOTESAPP_EXPORT_HMAC_KEY": key}):
                with self.assertRaises(RuntimeError):
                    sign_export(self.body)

    def test_cli_reports_pass_and_failure(self):
        script = Path(__file__).resolve().parents[1] / "export_integrity.py"
        for data, code, message in [
            (self.export, 0, b"CHECK PASSED\n"),
            (self.export.replace(b",14,", b",18,", 1), 1, b"CHECK FAILED\n"),
        ]:
            with self.subTest(code=code):
                result = subprocess.run(
                    [sys.executable, str(script)], input=data, capture_output=True,
                )
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(result.stdout, message)


if __name__ == "__main__":
    unittest.main()

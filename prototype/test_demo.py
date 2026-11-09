"""Check file-based automation without contacting a real mail provider."""

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_demo
from test_pipeline import PNG


class DemoTests(unittest.TestCase):
    """Exercise optional JSON handling and the single-send versus preview boundary."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.image = self.root / "meal.png"
        self.image.write_bytes(PNG)
        self.glucose = self.root / "glucose.json"
        self.args = ["--image", str(self.image), "--glucose", str(self.glucose)]

    def test_absent_glucose_remains_null(self):
        event, raw, subtype = run_demo.read_event(self.image, self.glucose, "demo")
        self.assertIsNone(event["glucose"])
        self.assertEqual((raw, subtype), (PNG, "png"))

    def test_existing_glucose_preserved(self):
        measurement = {"value": 7.2, "unit": "mmol/L", "measured_at": "2026-11-09T12:00:00+08:00"}
        self.glucose.write_text(json.dumps(measurement), encoding="utf-8-sig")
        event, raw, subtype = run_demo.read_event(self.image, self.glucose, "demo")
        self.assertEqual(event["glucose"], measurement)

    def test_preview_never_loads_mail_or_sends(self):
        with patch.object(run_demo, "load_mail_settings") as load, patch.object(run_demo.server, "send_email") as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_demo.main(self.args + ["--preview"]), 0)
            load.assert_not_called()
            send.assert_not_called()

    def test_normal_run_sends_once(self):
        with patch.object(run_demo, "load_mail_settings"), patch.object(run_demo.server, "send_email") as send, patch.dict(os.environ, {"SMTP_TO": "test@example.test"}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_demo.main(self.args), 0)
            send.assert_called_once()
            report, attachment, subtype = send.call_args.args
            self.assertIsNone(report["original_information"]["glucose"])
            self.assertEqual(attachment, PNG)

    def test_invalid_existing_json_prevents_send(self):
        self.glucose.write_text("{", encoding="utf-8")
        with patch.object(run_demo.server, "send_email") as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_demo.main(self.args), 1)
            send.assert_not_called()

    def test_invalid_reading_prevents_send(self):
        self.glucose.write_text('{"value": -1, "unit": "mmol/L", "measured_at": "2026-11-09T12:00:00Z"}')
        with patch.object(run_demo.server, "send_email") as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_demo.main(self.args), 1)
            send.assert_not_called()

    def test_mail_configuration_and_ca_loaded(self):
        settings = {"host": "smtp.example.test", "port": 587, "mode": "starttls", "user": "a@example.test",
                    "sender": "a@example.test", "recipient": "b@example.test", "password": "dummy-test-secret"}
        (self.root / ".env.smtp.json").write_text(json.dumps(settings), encoding="utf-8-sig")
        bundle = self.root / ".env.smtp-ca.pem"
        bundle.touch()
        with patch.object(run_demo, "ROOT", self.root), patch.dict(os.environ, {}, clear=True):
            run_demo.load_mail_settings()
            self.assertEqual(os.environ["SMTP_TO"], settings["recipient"])
            self.assertEqual(os.environ["SSL_CERT_FILE"], str(bundle))


if __name__ == "__main__":
    unittest.main()

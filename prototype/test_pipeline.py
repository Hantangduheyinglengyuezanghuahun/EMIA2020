"""Standard-library tests; no external email, credentials, downloads or AI calls."""

import base64
import copy
import http.client
import json
import os
import socketserver
import threading
import unittest
from contextlib import contextmanager
from email import policy
from email.parser import BytesParser
from http.server import HTTPServer
from unittest.mock import patch

import server

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="
)
EVENT = {
    "patient_id": "demo-patient-001", "meal_captured_at": "2026-11-09T12:00:00+08:00",
    "image": {"content_base64": base64.b64encode(PNG).decode("ascii")},
    "glucose": {"value": 7.2, "unit": "mmol/L", "measured_at": "2026-11-09T11:55:00+08:00"},
}
TOKEN = "local-test-token-only"


@contextmanager
def serving(instance):
    """Run a test-only server on a thread, then shut it down and close its socket."""
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield instance
    finally:
        instance.shutdown()
        thread.join(timeout=5)
        instance.server_close()


class SMTPReceiver(socketserver.StreamRequestHandler):
    """Minimal local SMTP fixture: capture DATA bytes; accept or reject delivery."""

    def handle(self):
        """Serve one SMTP session without authentication; retain its message in memory."""
        self.wfile.write(b"220 localhost test receiver\r\n")
        while True:
            line = self.rfile.readline()
            if not line:
                return
            command = line.split(b" ", 1)[0].strip().upper()
            if command == b"DATA":
                self.wfile.write(b"354 End with dot\r\n")
                parts = []
                while True:
                    part = self.rfile.readline()
                    if part in (b".\r\n", b""):
                        break
                    parts.append(part[1:] if part.startswith(b"..") else part)
                self.server.messages.append(b"".join(parts))
                self.wfile.write(b"550 Rejected for test\r\n" if self.server.reject else b"250 Accepted\r\n")
            elif command == b"QUIT":
                self.wfile.write(b"221 Bye\r\n")
                return
            else:
                self.wfile.write(b"250 OK\r\n")


class PipelineTests(unittest.TestCase):
    """Verify mock semantics, validation, HTTP behavior and real local SMTP transport."""

    def setUp(self):
        """Start an isolated HTTP server; each test gets independent state."""
        self.http = HTTPServer(("127.0.0.1", 0), server.Handler)
        self.http.api_token = TOKEN
        self.running = serving(self.http)
        self.running.__enter__()
        self.addCleanup(self.running.__exit__, None, None, None)

    def request(self, data=EVENT, path="/preview", token=TOKEN, content_type="application/json"):
        """POST JSON over a real loopback socket; return (HTTP status, parsed dict)."""
        connection = http.client.HTTPConnection("127.0.0.1", self.http.server_port, timeout=5)
        try:
            body = json.dumps(data).encode("utf-8")
            connection.request("POST", path, body, {"Content-Type": content_type,
                                                   "Authorization": "Bearer " + token})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_preview_preserves_original_and_marks_simulation(self):
        status, result = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(result["email_status"], "not_sent_preview")
        report = result["report"]
        self.assertEqual(report["original_information"]["glucose"], EVENT["glucose"])
        self.assertEqual(report["estimated_current_glucose"]["estimate"], 140)
        self.assertFalse(report["uncertainty"]["validated"])
        self.assertIsNone(report["uncertainty"]["confidence_level"])
        self.assertIn("Do not use", report["warning"])

    def test_missing_glucose_is_not_invented(self):
        event = copy.deepcopy(EVENT)
        del event["glucose"]
        status, result = self.request(event)
        self.assertEqual(status, 200)
        self.assertIsNone(result["report"]["original_information"]["glucose"])
        self.assertIn("not provided", result["report"]["suggestions"])

    def test_mgdl_and_jpeg_supported(self):
        event = copy.deepcopy(EVENT)
        event["glucose"].update(value=130, unit="mg/dL")
        event["image"]["content_base64"] = base64.b64encode(b"\xff\xd8\xfffixture").decode()
        normalized, raw, subtype = server.validate_event(event)
        self.assertEqual((normalized["glucose"]["value"], subtype), (130, "jpeg"))

    def test_rejects_invalid_measurements(self):
        for value in (-1, 0, True, "7.2", float("nan"), float("inf")):
            with self.subTest(value=value):
                event = copy.deepcopy(EVENT)
                event["glucose"]["value"] = value
                self.assertEqual(self.request(event)[0], 400)

    def test_rejects_bad_units_times_and_images(self):
        for section, field, value in (
            ("glucose", "unit", "unknown"), ("glucose", "measured_at", "2026-11-09T12:00:00"),
            ("image", "content_base64", "???"), ("image", "content_base64", "aGVsbG8="),
        ):
            with self.subTest(field=field):
                event = copy.deepcopy(EVENT)
                event[section][field] = value
                self.assertEqual(self.request(event)[0], 400)
        self.assertEqual(self.request([])[0], 400)

    def test_authentication_and_content_type(self):
        self.assertEqual(self.request(token="wrong")[0], 401)
        self.assertEqual(self.request(content_type="text/plain")[0], 415)
        self.assertEqual(self.request(path="/unknown")[0], 404)

    def test_body_limit(self):
        with patch.object(server, "MAX_BODY", 2):
            self.assertEqual(self.request()[0], 413)

    def test_health_and_malformed_json(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.http.server_port, timeout=5)
        try:
            connection.request("GET", "/health")
            response = connection.getresponse()
            self.assertEqual((response.status, json.loads(response.read())["status"]), (200, "ok"))
            connection.request("POST", "/preview", b"{", {"Content-Type": "application/json",
                                                          "Authorization": "Bearer " + TOKEN})
            response = connection.getresponse()
            self.assertEqual(response.status, 400)
            response.read()
        finally:
            connection.close()

    def smtp_roundtrip(self, reject=False):
        """POST an event through HTTP and real SMTP to a private in-memory receiver."""
        receiver = socketserver.TCPServer(("127.0.0.1", 0), SMTPReceiver)
        receiver.messages, receiver.reject = [], reject
        with serving(receiver), patch.dict(os.environ, {
            "SMTP_HOST": "127.0.0.1", "SMTP_PORT": str(receiver.server_address[1]),
            "SMTP_MODE": "plain", "SMTP_FROM": "sender@example.test", "SMTP_TO": "caregiver@example.test",
        }, clear=True):
            status, result = self.request(path="/events")
        return status, result, receiver.messages

    def test_real_smtp_delivery_and_attachment(self):
        status, result, messages = self.smtp_roundtrip()
        self.assertEqual((status, result["email_status"], len(messages)), (200, "accepted_by_smtp", 1))
        message = BytesParser(policy=policy.default).parsebytes(messages[0])
        self.assertEqual(message["To"], "caregiver@example.test")
        self.assertIn("SIMULATED DEMO", message["Subject"])
        attachment, = list(message.iter_attachments())
        self.assertEqual(attachment.get_payload(decode=True), PNG)
        self.assertEqual(attachment.get_content_type(), "image/png")
        self.assertIn('"value": 7.2', message.get_body(preferencelist=("plain",)).get_content())

    def test_smtp_rejection_is_failure(self):
        status, result, messages = self.smtp_roundtrip(reject=True)
        self.assertEqual((status, result["email_status"]), (502, "failed_or_unconfirmed"))

    def test_missing_smtp_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.request(path="/events")[0], 502)

    def test_remote_plaintext_smtp_blocked(self):
        with patch.dict(os.environ, {"SMTP_HOST": "example.test", "SMTP_MODE": "plain",
                                   "SMTP_FROM": "a@example.test", "SMTP_TO": "b@example.test"}, clear=True):
            with self.assertRaises(ValueError):
                server.smtp_settings()

    def test_starttls_and_login_are_used(self):
        event, raw, subtype = server.validate_event(EVENT)
        with patch.dict(os.environ, {"SMTP_HOST": "example.test", "SMTP_FROM": "a@example.test",
                                   "SMTP_TO": "b@example.test", "SMTP_USER": "test-user",
                                   "SMTP_PASSWORD": "test-secret"}, clear=True), patch.object(server.smtplib, "SMTP") as smtp:
            server.send_email(server.analyze(event, raw), raw, subtype)
            client = smtp.return_value.__enter__.return_value
            client.starttls.assert_called_once()
            client.login.assert_called_once_with("test-user", "test-secret")
            client.send_message.assert_called_once()


if __name__ == "__main__":
    unittest.main()
